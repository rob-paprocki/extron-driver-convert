from extronlib.interface import EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.Models = {
            }

        self.Commands = {
            'CUERecall'         : {'Status': {}},
            }

    def SetCUERecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            CUERecallCmdString = 'cue {0}'.format(value)
            self.__SetHelper('CUERecall', CUERecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCUERecall')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

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
