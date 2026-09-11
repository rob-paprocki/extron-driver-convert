from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FaderLevel': {'Parameters': ['Channel'], 'Status': {}},
            'FaderLevelStep': {'Parameters': ['Channel'], 'Status': {}},
            'Line4Select': {'Status': {}},
            'Mute': {'Parameters': ['Channel'], 'Status': {}},
            'ParallelOutput': {'Parameters': ['Channel'], 'Status': {}},
            'SceneRecall': {'Status': {}},
        }

    def SetFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Master A': '@',
            'Master B': 'A',
            'Remote 1': 'B',
            'Remote 2': 'C',
            'Remote 3': 'D',
            'Remote 4': 'E',
            'Remote 5': 'F',
            'Remote 6': 'G'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 60
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FaderLevelCmdString = 'CLVL{0}{1}\r'.format(ChannelStates[qualifier['Channel']], chr(value + 48))
            self.__SetHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFaderLevel')

    def SetFaderLevelStep(self, value, qualifier):

        ChannelStates = {
            'Mic 1/WL1 Input': '0',
            'Mic 2/WL2 Input': '1',
            'Mic 3 Input': '2',
            'Mic 4 Input': '3',
            'Mic 5/Line 1 Input': '4',
            'Mic 6/Line 2 Input': '5',
            'Line 3': '6',
            'Line 4': '7',
            'Line Output 1': '8',
            'Line Output 2': '9',
            'Line Output 3': ':',
            'Line Output 4': ';',
            'Line Output 5': '<',
            'Line Output 6': '=',
            'Line Output 7': '>',
            'Line Output 8': '?'
        }

        ValueStateValues = {
            'Up': 'CLV+',
            'Down': 'CLV-',
            'Stop': 'CLVS'
        }

        FaderLevelStepCmdString = '{0}{1}\r'.format(ValueStateValues[value], ChannelStates[qualifier['Channel']])
        self.__SetHelper('FaderLevelStep', FaderLevelStepCmdString, value, qualifier)

    def SetLine4Select(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'A': '1',
            'B': '2',
            'C': '3',
            'D': '4',
            'E': '5',
            'F': '6'
        }

        Line4SelectCmdString = 'CSEL{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Line4Select', Line4SelectCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ChannelStates = {
            'Mic 1/WL1 Input': '0',
            'Mic 2/WL2 Input': '1',
            'Mic 3 Input': '2',
            'Mic 4 Input': '3',
            'Mic 5/Line 1 Input': '4',
            'Mic 6/Line 2 Input': '5',
            'Line 3': '6',
            'Line 4': '7',
            'Line Output 1': '8',
            'Line Output 2': '9',
            'Line Output 3': ':',
            'Line Output 4': ';',
            'Line Output 5': '<',
            'Line Output 6': '=',
            'Line Output 7': '>',
            'Line Output 8': '?',
            'Master A': '@',
            'Master B': 'A',
            'Remote 1': 'B',
            'Remote 2': 'C',
            'Remote 3': 'D',
            'Remote 4': 'E',
            'Remote 5': 'F',
            'Remote 6': 'G'
        }

        ValueStateValues = {
            'On': 'A',
            'Off': '@'
        }

        MuteCmdString = 'CMUT{0}{1}\r'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetParallelOutput(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': ':'
        }

        ValueStateValues = {
            'On': 'CPON',
            'Off': 'CPOF'
        }

        ParallelOutputCmdString = '{0}{1}\r'.format(ValueStateValues[value], ChannelStates[qualifier['Channel']])
        self.__SetHelper('ParallelOutput', ParallelOutputCmdString, value, qualifier)

    def SetSceneRecall(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': ':',
            '11': ';',
            '12': '<',
            '13': '=',
            '14': '>',
            '15': '?',
            '16': '@',
            '17': 'A',
            '18': 'B',
            '19': 'C',
            '20': 'D'
        }

        SceneRecallCmdString = 'CRCL{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
