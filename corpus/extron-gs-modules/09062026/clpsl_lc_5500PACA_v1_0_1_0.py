from extronlib.interface import SerialInterface, EthernetClientInterface
class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Power': {'Parameters':['Group'], 'Status':{}},
            }

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : '79',
            'Off' : '01',
            }

        GroupConstraints = {
            'Min' : 1,
            'Max' : 255,
            }

        groupNumber = int(qualifier['Group']) 
            
        if GroupConstraints['Min'] <= groupNumber <= GroupConstraints['Max']:
            group = hex(groupNumber).split('x')
            group = group[1].upper().zfill(2)
            PowerCmdString = '\\053800{0}{1}\r'.format(PowerStateValues[value], group)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPower')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
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