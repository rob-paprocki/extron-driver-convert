from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ExecutiveMode': {'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'ReverttoPreviousSwitchState': {'Status': {}},
        }

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '/%Lock;',
            'Off': '/%Unlock;'
        }

        self.__SetHelper('ExecutiveMode', States[value], value, qualifier)

    def SetMatrixTieCommand(self, value, qualifier):

        input_state = qualifier['Input']
        output_state = qualifier['Output']

        CmdString = ''
        if input_state == 'Break' and output_state == 'All':
            CmdString = 'All$.'
        elif input_state != 'Break' and output_state == 'All' and 1 <= int(input_state) <= 4:
            CmdString = '{0}All.'.format(input_state)
        elif input_state == 'Break' and output_state != 'All' and 1 <= int(output_state) <= 4:
            CmdString = '{0}$.'.format(output_state)
        elif 1 <= int(input_state) <= 4 and 1 <= int(output_state) <= 4:
            CmdString = '{0}B{1}.'.format(input_state, output_state)
        if CmdString:
            self.__SetHelper('MatrixTieCommand', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixTieCommand')

    def SetPreset(self, value, qualifier):

        Actions = {
            'Recall': 'Recall',
            'Save': 'Save',
            'Delete': 'Clear'
        }

        Action = Actions[qualifier['Action']]
        if 1 <= int(value) <= 10 and Action:
            Preset = int(value) - 1
            CmdString = '{0}{1}.'.format(Action, Preset)
            self.__SetHelper('Preset', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def SetReverttoPreviousSwitchState(self, value, qualifier):
        self.__SetHelper('ReverttoPreviousSwitchState', 'Undo.', value, qualifier)

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
