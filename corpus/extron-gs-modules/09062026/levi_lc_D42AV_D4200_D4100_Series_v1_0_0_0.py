from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DimmerFadeRate': {'Status': {}},
            'DimmerLevel': {'Parameters': ['Dimmer Number'], 'Status': {}},
            'Dimming': {'Parameters': ['Dimmer Number'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Net ID'], 'Status': {}},
        }

    def SetDimmerFadeRate(self, value, qualifier):

        ValueStateValues = {
            'Photocell Capture or Record': '253',
            'Photocell On': '254',
            'Stop Fade': '255'
        }

        if value.isdigit():
            if 0 <= int(value) <= 239:
                DimmerFadeRateCmdString = 'F{0}\r\n'.format(value)
                self.__SetHelper('DimmerFadeRate', DimmerFadeRateCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDimmerFadeRate')
        else:
            DimmerFadeRateCmdString = 'F{0}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('DimmerFadeRate', DimmerFadeRateCmdString, value, qualifier)

    def SetDimmerLevel(self, value, qualifier):

        DimmerNumberConstraints = {
            'Min': 1,
            'Max': 2048
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        dim_num = qualifier['Dimmer Number']
        if DimmerNumberConstraints['Min'] <= dim_num <= DimmerNumberConstraints['Max'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            DimmerLevelCmdString = 'D{0}@{1}\r\n'.format(dim_num, value)
            self.__SetHelper('DimmerLevel', DimmerLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmerLevel')

    def SetDimming(self, value, qualifier):

        DimmerNumberConstraints = {
            'Min': 1,
            'Max': 2048
        }

        ValueStateValues = {
            'Off': 'L',
            'Max': 'R',
            'Stop': 'S'
        }

        dim_num = qualifier['Dimmer Number']
        if DimmerNumberConstraints['Min'] <= dim_num <= DimmerNumberConstraints['Max']:
            DimmerCmdString = ValueStateValues[value] + str(dim_num) + '\r\n'
            self.__SetHelper('Dimming', DimmerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimming')

    def SetPresetRecall(self, value, qualifier):

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
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            'Off': '18'
        }

        net_id = qualifier['Net ID']
        if 1 <= int(net_id) <= 127:
            PresetRecallCmdString = 'P{0}@{1}\r\n'.format(ValueStateValues[value], net_id)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
        # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
