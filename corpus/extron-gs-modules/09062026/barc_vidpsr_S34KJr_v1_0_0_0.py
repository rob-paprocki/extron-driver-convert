from extronlib.interface import EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AutoTransition': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
        }

    def SetAutoTransition(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 1999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AutoTransitionCmdString = 'ATRN {0}'.format(value)
            self.__SetHelper('AutoTransition', AutoTransitionCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAutoTransition')

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 1000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PresetRecallCmdString = 'PRESET -r {0}'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 1000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PresetSaveCmdString = 'PRESET -s {0}'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

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
