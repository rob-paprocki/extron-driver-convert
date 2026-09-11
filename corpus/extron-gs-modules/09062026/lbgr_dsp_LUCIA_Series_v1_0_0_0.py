from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {
            'LUCIA 120/2': self.lbgr_25_2714_regular,
            'LUCIA 240/2': self.lbgr_25_2714_regular,
            'LUCIA 120/2M': self.lbgr_25_2714_M,
            'LUCIA 240/2M': self.lbgr_25_2714_M,
            'LUCIA 120/1-70': None,
            'LUCIA 240/1-70': None,
            'LUCIA 60/2M': self.lbgr_25_2714_M,
            'LUCIA 60/2': self.lbgr_25_2714_regular,
            'LUCIA 60/1-70': None,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FullMatrixRecall': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'FullMatrixRecall70': {'Parameters': ['Input'], 'Status': {}},
            'MatrixPatchPointGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixPatchPointGain70': {'Parameters': ['Input'], 'Status': {}},
            'OutputMuteAll': {'Status': {}},
            'OutputVolume': {'Parameters': ['Output'], 'Status': {}},
            'OutputVolume70': {'Status': {}},
            'Power': {'Status': {}},
        }

    def SetFullMatrixRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': -31,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FullMatrixRecallCmdString = 'setmatrix {0},{1},{2}\r'.format(self.InputStates[qualifier['Input']], self.OutputStates[qualifier['Output']], value)
            self.__SetHelper('FullMatrixRecall', FullMatrixRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFullMatrixRecall')

    def SetFullMatrixRecall70(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2'
        }

        ValueConstraints = {
            'Min': -31,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FullMatrixRecallCmdString = 'setmatrix {0},1,{1}\r'.format(InputStates[qualifier['Input']], value)
            self.__SetHelper('FullMatrixRecall70', FullMatrixRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFullMatrixRecall70')

    def SetMatrixPatchPointGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -31,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MatrixPatchPointGainCmdString = 'setpatchpoint {0},{1},{2}\r'.format(self.InputStates[qualifier['Input']], self.OutputStates[qualifier['Output']], value)
            self.__SetHelper('MatrixPatchPointGain', MatrixPatchPointGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixPatchPointGain')

    def SetMatrixPatchPointGain70(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2'
        }

        ValueConstraints = {
            'Min': -31,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MatrixPatchPointGainCmdString = 'setpatchpoint {0},1,{1}\r'.format(InputStates[qualifier['Input']], value)
            self.__SetHelper('MatrixPatchPointGain70', MatrixPatchPointGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixPatchPointGain70')

    def SetOutputMuteAll(self, value, qualifier):

        ValueStateValues = {
            'On': 'mute 1\r',
            'Off': 'mute 0\r'
        }

        OutputMuteAllCmdString = ValueStateValues[value]
        self.__SetHelper('OutputMuteAll', OutputMuteAllCmdString, value, qualifier)

    def SetOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputVolumeCmdString = 'setvolume {0} {1}\r'.format(self.OutputStates[qualifier['Output']], value)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputVolume')

    def SetOutputVolume70(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputVolumeCmdString = 'setvolume 1 {0}\r'.format(value)
            self.__SetHelper('OutputVolume70', OutputVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputVolume70')

    def SetPower(self, value, qualifier):

        cmdstring = ''.ljust(20) if value == 'On' else 'standby\r'
        PowerCmdString = cmdstring
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def lbgr_25_2714_regular(self):

        self.InputStates = {
            '1': '1',
            '2': '2'
        }

        self.OutputStates = {
            '1': '1',
            '2': '2'
        }

    def lbgr_25_2714_M(self):

        self.InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        self.OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }
        
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
