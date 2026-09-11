from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {
            'AC-MX-44HDBT': self.avpro_15_6001_44,
            'AC-MX-88HDBT': self.avpro_15_6001_88,
        }

        self.Commands = {
            'ExecutiveMode': { 'Status': {}},
            'HDBTOutputAudioMute': {'Parameters':['Output'], 'Status': {}},
            'HDBTOutputVideoMode': {'Parameters':['Output'], 'Status': {}},
            'HDMIOutputAudioMute': {'Parameters':['Output'], 'Status': {}},
            'HDMIOutputVideoMode': {'Parameters':['Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
        }

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'SET KEY LOCK {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetHDBTOutputAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if qualifier['Output'] in self.OutputStates and value in ValueStateValues:
            HDBTOutputAudioMuteCmdString = 'SET OUT{} TP HA MUTE {}\r'.format(self.OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('HDBTOutputAudioMute', HDBTOutputAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDBTOutputAudioMute')

    def SetHDBTOutputVideoMode(self, value, qualifier):

        ValueStateValues = {
            '4K to 2K': '2',
            'ICT Mode': '5'
        }

        if qualifier['Output'] in self.OutputStates and value in ValueStateValues:
            HDBTOutputVideoModeCmdString = 'SET OUT{} TP VIDEO{}\r'.format(self.OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('HDBTOutputVideoMode', HDBTOutputVideoModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDBTOutputVideoMode')
            
    def SetHDMIOutputAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if qualifier['Output'] in self.OutputStates and value in ValueStateValues:
            HDMIOutputAudioMuteCmdString = 'SET OUT{} HP HA MUTE {}\r'.format(self.OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('HDMIOutputAudioMute', HDMIOutputAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIOutputAudioMute')

    def SetHDMIOutputVideoMode(self, value, qualifier):

        ValueStateValues = {
            'Bypass': '1',
            '2K to 4K': '3'
        }

        if qualifier['Output'] in self.OutputStates and value in ValueStateValues:
            HDMIOutputVideoModeCmdString = 'SET OUT{} HP VIDEO{}\r'.format(self.OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('HDMIOutputVideoMode', HDMIOutputVideoModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIOutputVideoMode')

    def SetMatrixTieCommand(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputMax and qualifier['Output'] in self.OutputStates:
            MatrixTieCommandCmdString = 'SET OUT{} VS IN{}\r'.format(self.OutputStates[qualifier['Output']], qualifier['Input'])
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def avpro_15_6001_44(self):

        self.InputMax = 4
        self.OutputStates = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            'All': '0'
        }

    def avpro_15_6001_88(self):

        self.InputMax = 8
        self.OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            'All': '0'
        }

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