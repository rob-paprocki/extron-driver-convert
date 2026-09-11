from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AudioMute': {'Parameters': ['Output', 'Type'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'InputEDID': {'Parameters': ['Input'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            '1':    '1',
            '2':    '2',
            '3':    '3',
            '4':    '4',
            'All':  '0'
        }
        output = qualifier['Output']

        TypeStates = {
            'HDMI':     'HP',
            'HDBaseT':  'TP'
        }
        type_ = qualifier['Type']

        ValueStateValues = {
            'On',
            'Off'
        }

        if output in OutputStates and type_ in TypeStates and value in ValueStateValues:
            AudioMuteCmdString = 'SET OUT{} {} HA MUTE {}\r'.format(OutputStates[output], TypeStates[type_], value.upper())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On',
            'Off'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'SET KEY LOCK {}\r'.format(value.upper())
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetInputEDID(self, value, qualifier):

        InputStates = {
            '1':    '1',
            '2':    '2',
            '3':    '3',
            '4':    '4',
            'All':  '0'
        }
        input_ = qualifier['Input']

        ValueStateValues = {
            '1080P_2CH':                '0',
            '1080P_6CH':                '1',
            '1080P_8CH':                '2',
            '1080P_3D_2CH':             '3',
            '1080P_3D_6CH':             '4',
            '1080P_3D_8CH':             '5',
            '4K30HZ_3D_2CH':            '6',
            '4K30HZ_3D_6CH':            '7',
            '4K30HZ_3D_8CH':            '8',
            '4K60HzY420_3D_2CH':        '9',
            '4K60HzY420_3D_6CH':        '10',
            '4K60HzY420_3D_8CH':        '11',
            '4K60Hz_3D_2CH':            '12',
            '4K60Hz_3D_6CH':            '13',
            '4K60Hz_3D_8CH':            '14',
            '1080P_2CH_HDR':            '15',
            '1080P_6CH_HDR':            '16',
            '1080P_8CH_HDR':            '17',
            '1080P_3D_2CH_HDR':         '18',
            '1080P_3D_6CH_HDR':         '19',
            '1080P_3D_8CH_HDR':         '20',
            '4K30HZ_3D_2CH_HDR':        '21',
            '4K30HZ_3D_6CH_HDR':        '22',
            '4K30HZ_3D_8CH_HDR':        '23',
            '4K60HzY420_3D_2CH_HDR':    '24',
            '4K60HzY420_3D_6CH_HDR':    '25',
            '4K60HzY420_3D_8CH_HDR':    '26',
            '4K60HZ_3D_2CH_HDR':        '27',
            '4K60HZ_3D_6CH_HDR':        '28',
            '4K60HZ_3D_8CH_HDR':        '29',
            'User EDID 1':              '30',
            'User EDID 2':              '31',
            'User EDID 3':              '32'
        }

        if input_ in InputStates and value in ValueStateValues:
            InputEDIDCmdString = 'SET IN{} EDID {}\r'.format(InputStates[input_], ValueStateValues[value])
            self.__SetHelper('InputEDID', InputEDIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputEDID')

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = int(qualifier['Input'])

        OutputStates = {
            '1':    '1',
            '2':    '2',
            '3':    '3',
            '4':    '4',
            'All':  '0'
        }
        output = qualifier['Output']

        TieTypeStates = {
            'Video': 'VS',
            'Audio': 'AS'
        }
        tie_type = qualifier['Tie Type']

        if 1 <= input_ <= 4 and output in OutputStates and tie_type in TieTypeStates:
            MatrixTieCommandCmdString = 'SET OUT{} {} IN{}\r'.format(OutputStates[output], TieTypeStates[tie_type], input_)
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetVolume(self, value, qualifier):

        OutputStates = {
            '1':    '1',
            '2':    '2',
            '3':    '3',
            '4':    '4',
            'All':  '0'
        }
        output = qualifier['Output']

        if output in OutputStates and 0 <= value <= 100:
            VolumeCmdString = 'SET OUT{} EXAUD LEV{}\r'.format(OutputStates[output], value)
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