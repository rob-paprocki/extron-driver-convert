from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DimmerDiscrete': {'Parameters': ['Maingroup', 'Midgroup', 'Subgroup'], 'Status': {}},
            'DimmerStep': {'Parameters': ['Maingroup', 'Midgroup', 'Subgroup'], 'Status': {}},
        }        

    def SetDimmerDiscrete(self, value, qualifier):

        Maingroup = int(qualifier['Maingroup'])
        Midgroup = int(qualifier['Midgroup'])
        Subgroup = int(qualifier['Subgroup'])

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        MaingroupConstraints = {
            'Min': 0,
            'Max': 15
        }

        MidgroupConstraints = {
            'Min': 0,
            'Max': 7
        }

        SubgroupConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if MaingroupConstraints['Min'] <= Maingroup <= MaingroupConstraints['Max']:
                if MidgroupConstraints['Min'] <= Midgroup <= MidgroupConstraints['Max']:
                    if SubgroupConstraints['Min'] <= Subgroup <= SubgroupConstraints['Max']:
                        DimmerDiscreteCmdString = '{0}/{1}/{2}={3}\r'.format(Maingroup, Midgroup, Subgroup, value)
                        self.__SetHelper('DimmerDiscrete', DimmerDiscreteCmdString, value, qualifier)
                    else:
                        print('Invalid Command for SetDimmerDiscrete')
                else:
                    print('Invalid Command for SetDimmerDiscrete')
            else:
                print('Invalid Command for SetDimmerDiscrete')
        else:
            print('Invalid Command for SetDimmerDiscrete')

    def SetDimmerStep(self, value, qualifier):

        Maingroup = int(qualifier['Maingroup'])
        Midgroup = int(qualifier['Midgroup'])
        Subgroup = int(qualifier['Subgroup'])

        ValueStateValues = {
            'Up': '9',
            'Down': '1',
            'Stop': '0'
        }

        MaingroupConstraints = {
            'Min': 0,
            'Max': 15
        }

        MidgroupConstraints = {
            'Min': 0,
            'Max': 7
        }

        SubgroupConstraints = {
            'Min': 0,
            'Max': 255
        }

        if MaingroupConstraints['Min'] <= Maingroup <= MaingroupConstraints['Max']:
            if MidgroupConstraints['Min'] <= Midgroup <= MidgroupConstraints['Max']:
                if SubgroupConstraints['Min'] <= Subgroup <= SubgroupConstraints['Max']:
                    DimmerStepCmdString = '{0}/{1}/{2}={3}\r'.format(Maingroup, Midgroup, Subgroup, ValueStateValues[value])
                    self.__SetHelper('DimmerStep', DimmerStepCmdString, value, qualifier)
                else:
                    print('Invalid Command for SetDimmerStep')
            else:
                print('Invalid Command for SetDimmerStep')
        else:
            print('Invalid Command for SetDimmerStep')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        
        self.Send(commandstring)
        print(commandstring)

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
