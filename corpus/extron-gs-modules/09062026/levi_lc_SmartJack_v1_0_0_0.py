from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Dimmer': {'Parameters': ['Fade Time', 'Fade Rate', 'Channel', 'Panel'], 'Status': {}},
            'Scene': {'Parameters': ['Fade Time', 'Fade Rate', 'Group'], 'Status': {}},
        }


    def EscapeCommand(self, oldStr):
        newStr = b''
        for val in oldStr[1:-2]:
            if val == 33:
                newStr += b'\x21\x21'
            else:
                newStr += pack('>B', val)
        return oldStr[0:1] + newStr + oldStr[-2:]

    def SetDimmer(self, value, qualifier):

        FadeTimeConstraints = {
            'Min': 0,
            'Max': 126
        }

        FadeRateStates = {
            'Minutes': 1,
            'Seconds': 0,
            'Default': b'\xff'
        }

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x02',
            'Dim': b'\x04',
            'Bright': b'\x08',
            'Preset': b'\x40',
            'Program': b'\x80'
        }
        failedCondition = False

        DimmerCmdString = b'\x21\x30\x04'
        NonCmdString = b'\x21\x30\x04'
        if qualifier['Panel'] == 'Broadcast' and qualifier['Channel'] == 'Broadcast':
            DimmerCmdString += b'\x00'
            NonCmdString += b'\x00'
        elif qualifier['Panel'] == 'Broadcast' or qualifier['Channel'] == 'Broadcast':
            failedCondition = True
        elif 1 <= int(qualifier['Panel']) <= 31 and 1 <= int(qualifier['Channel']) <= 7:
            DimmerCmdString += pack('>B', int(qualifier['Panel']) * 8 + int(qualifier['Channel']))
            NonCmdString += pack('>B', int(qualifier['Panel']) * 8 + int(qualifier['Channel']))
        else:
            failedCondition = True

        DimmerCmdString += b'\x00\x00'
        NonCmdString += b'\x00\x00\x00'

        if value in ValueStateValues:
            DimmerCmdString += ValueStateValues[value]
        else:
            failedCondition = True

        if qualifier['Fade Rate'] == 'Default':
            DimmerCmdString += FadeRateStates[qualifier['Fade Rate']]
            NonCmdString += FadeRateStates[qualifier['Fade Rate']]
        elif qualifier['Fade Time'] == 0:
            DimmerCmdString += b'\x00'
            NonCmdString += b'\x00'
        elif FadeTimeConstraints['Min'] <= qualifier['Fade Time'] <= FadeTimeConstraints['Max']:
            DimmerCmdString += pack('>B', qualifier['Fade Time'] + FadeRateStates[qualifier['Fade Rate']])
            NonCmdString += pack('>B', qualifier['Fade Time'] + FadeRateStates[qualifier['Fade Rate']])
        else:
            failedCondition = True

        DimmerCmdString += b'\x00\x21\x10'
        NonCmdString += b'\x00\x21\x10'
        DimmerCmdString = self.EscapeCommand(DimmerCmdString)
        NonCmdString = self.EscapeCommand(NonCmdString)
        
        if not failedCondition:
            self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)
            self.__SetHelper('Dimmer', NonCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDimmer')

    def SetScene(self, value, qualifier):

        FadeTimeConstraints = {
            'Min': 0,
            'Max': 126
        }

        FadeRateStates = {
            'Minutes': 128,
            'Seconds': 0,
            'Default': b'\xff'
        }

        ValueStateValues = {
            'Max': b'\x75',
            'On': b'\x7e',
            'Off': b'\x7d',
            'Dim': b'\x7c',
            'Bright': b'\x7b',
            'Stop': b'\x7f',
            'Non': b'\x7a',
            'Lock': b'\x79',
            'Unlock': b'\x78',
            'Set': b'\x77'
        }

        SceneCmdString = b'\x21\x30\x03\x00\x00'

        failedCondition = False

        if qualifier['Group'] == 'Broadcast':
            SceneCmdString += b'\xff'
        elif 0 <= int(qualifier['Group']) <= 63:
            SceneCmdString += pack('>B', int(qualifier['Group']))
        else:
            failedCondition = True

        if value in ValueStateValues:
            SceneCmdString += ValueStateValues[value]
        elif 0 <= int(value) <= 31:
            SceneCmdString += pack('>B', int(value))
        else:
            failedCondition = True

        if qualifier['Fade Rate'] == 'Default':
            SceneCmdString += FadeRateStates[qualifier['Fade Rate']]
        elif qualifier['Fade Time'] == 0:
            SceneCmdString += b'\x00'
        elif FadeTimeConstraints['Min'] <= qualifier['Fade Time'] <= FadeTimeConstraints['Max']:
            SceneCmdString += pack('>B', qualifier['Fade Time'] + FadeRateStates[qualifier['Fade Rate']])
        else:
            failedCondition = True

        SceneCmdString += b'\x21\x10'
        SceneCmdString = self.EscapeCommand(SceneCmdString)
        
        if not failedCondition:
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            print('Invalid Command for SetScene')

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
