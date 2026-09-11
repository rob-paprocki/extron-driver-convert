from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'MatrixCommand': {'Parameters': ['Mute', 'Output', 'Input'], 'Status': {}},
            'Mute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Channel'], 'Status': {}}
        }

    def SetMatrixCommand(self, value, qualifier):

        MuteStates = {
            'On': 'MUTE',
            'Off': 'UNMUTE'
        }

        OutputStates = ['1', '2']
        InputStates = ['1', '2', '3', '4', '5', '6', '7', '8']

        mute = qualifier['Mute']
        output = qualifier['Output']
        input_ = qualifier['Input']
        if mute in MuteStates and output in OutputStates and input_ in InputStates:
            MatrixCommandCmdString = '#MATRIX:DB={0};CH={1};CH_IN={2};\x5C'.format(MuteStates[mute], output, input_)
            self.__SetHelper('MatrixCommand', MatrixCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixCommand')

    def SetMute(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            'Both': ''
        }

        ValueStateValues = {
            'On': 'MUTE',
            'Off': 'UNMUTE'
        }

        output = qualifier['Output']
        if output in OutputStates:
            MuteCmdString = '#{0}{1}:\x5C'.format(ValueStateValues[value], OutputStates[output])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMute')

    def SetVolume(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            'Master': 'MASTER'
        }

        ValueStateValues = {
            'Up': '+',
            'Down': '-'
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            VolumeCmdString = '#VOL:INC={0}1;CH={1};\x5C'.format(ValueStateValues[value], ChannelStates[channel])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

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

    def __init__(self, Host, Port, Baud=4800, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
