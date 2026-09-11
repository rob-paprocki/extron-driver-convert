from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'MatrixTieCommand'  : {'Parameters':['Input','Output'], 'Status': {}},
            'Preset'            : {'Parameters':['Action'], 'Status': {}},
            }

    def SetMatrixTieCommand(self, value, qualifier):

        InVal  = qualifier['Input']
        OutVal = qualifier['Output']

        if (InVal in ['Break', '1', '2', '3', '4']) and (OutVal in ['1', '2', '3', '4']):
            if InVal == 'Break':
                InVal = '0'       
            CmdString = 'I{0}>O{1}\r'.format(InVal, OutVal)
            self.__SetHelper('MatrixTieCommand', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetPreset(self, value, qualifier):

        States = {
                  'Set': {
                            '1' : b'\x50\x01\x0A',
                            '2' : b'\x50\x02\x0B',
                            '3' : b'\x50\x03\x0C',
                            '4' : b'\x50\x04\x0D',
                            },

                  'Recall' : {
                            '1' : b'\x51\x01\x0B',
                            '2' : b'\x51\x02\x0C',
                            '3' : b'\x51\x03\x0D',
                            '4' : b'\x51\x04\x0E',
                            }
                  }

        CmdString = b'\x0B\x4D\x41\x52\x44\x43\x48\xFF' + States[qualifier['Action']][value]
        self.__SetHelper('Preset', CmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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