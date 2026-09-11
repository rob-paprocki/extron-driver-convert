from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AuxMute': {'Parameters': ['Number'], 'Status': {}},
            'AuxVolume': {'Parameters': ['Number'], 'Status': {}},
            'BusMute': {'Parameters': ['Number'], 'Status': {}},
            'BusVolume': {'Parameters': ['Number'], 'Status': {}},
            'ChannelMute': {'Parameters': ['Number'], 'Status': {}},
            'ChannelVolume': {'Parameters': ['Number'], 'Status': {}},
            'MasterMute': { 'Status': {}},
            'MasterVolume': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            }

    def SetAuxMute(self, value, qualifier):

        NumberStates = {
            '1': 0x6F,
            '2': 0x70,
            '3': 0x71,
            '4': 0x72,
            '5': 0x73,
            '6': 0x74,
            '7': 0x75,
            '8': 0x76,
        }

        ValueStateValues = {
            'On':  0x7F,
            'Off': 0x00,
        }

        aux_select = qualifier['Number']
        if aux_select in NumberStates and value in ValueStateValues:
            AuxMuteCmdString = pack('>BBB', 0xB1, NumberStates[aux_select], ValueStateValues[value])
            self.__SetHelper('AuxMute', AuxMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxMute')
    def SetAuxVolume(self, value, qualifier):

        NumberStates = {
            '1': 0x15,
            '2': 0x16,
            '3': 0x17,
            '4': 0x18,
            '5': 0x19,
            '6': 0x1A,
            '7': 0x1B,
            '8': 0x1C
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 127
        }

        aux_select = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and aux_select in NumberStates:
            AuxVolumeCmdString = pack('>BBB', 0xB1, NumberStates[aux_select], value)
            self.__SetHelper('AuxVolume', AuxVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxVolume')

    def SetBusMute(self, value, qualifier):

        NumberStates = {
            '1': 0x4C,
            '2': 0x4D,
            '3': 0x4E,
            '4': 0x4F,
            '5': 0x50,
            '6': 0x51,
            '7': 0x52,
            '8': 0x53
        }

        ValueStateValues = {
            'On':  0x7F,
            'Off': 0x00
        }

        bus_select = qualifier['Number']
        if bus_select in NumberStates and value in ValueStateValues:
            BusMuteCmdString = pack('>BBB', 0xB1, NumberStates[bus_select], ValueStateValues[value])
            self.__SetHelper('BusMute', BusMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusMute')
    def SetBusVolume(self, value, qualifier):

        NumberStates = {
            '1': 0x0D,
            '2': 0x0E,
            '3': 0x0F,
            '4': 0x10,
            '5': 0x11,
            '6': 0x12,
            '7': 0x13,
            '8': 0x14
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 127
        }

        bus_select = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and bus_select in NumberStates:
            BusVolumeCmdString = pack('>BBB', 0xB1, NumberStates[bus_select], value)
            self.__SetHelper('BusVolume', BusVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusVolume')

    def SetChannelMute(self, value, qualifier):

        NumberStates = {
            '1':  0x40,
            '2':  0x41,
            '3':  0x42,
            '4':  0x43,
            '5':  0x44,
            '6':  0x45,
            '7':  0x46,
            '8':  0x47,
            '9':  0x48,
            '10': 0x49,
            '11': 0x4A,
            '12': 0x4B,
            '13': 0x4C,
            '14': 0x4D,
            '15': 0x4E,
            '16': 0x4F
        }

        ValueStateValues = {
            'On':  0x7F,
            'Off': 0x00
        }

        channel_select = qualifier['Number']
        if channel_select in NumberStates and value in ValueStateValues:
            ChannelMuteCmdString = pack('>BBB', 0xB0, NumberStates[channel_select], ValueStateValues[value])
            self.__SetHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMute')
    def SetChannelVolume(self, value, qualifier):

        NumberStates = {
            '1':  0x01,
            '2':  0x02,
            '3':  0x03,
            '4':  0x04,
            '5':  0x05,
            '6':  0x06,
            '7':  0x07,
            '8':  0x08,
            '9':  0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 127
        }

        channel_select = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_select in NumberStates:
            ChannelVolumeCmdString = pack('>BBB', 0xB0, NumberStates[channel_select], value)
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelVolume')

    def SetMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On':  0x7F,
            'Off': 0x00
        }
        if value in ValueStateValues:
            MasterMuteCmdString = pack('>BBB', 0xB1, 0x1E, ValueStateValues[value])
            self.__SetHelper('MasterMute', MasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterMute')
    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 127
        }
        
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = pack('>BBB', 0xB0, 0x1E, value)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1':  0x00,
            '2':  0x01,
            '3':  0x02,
            '4':  0x03,
            '5':  0x04,
            '6':  0x05,
            '7':  0x06,
            '8':  0x07,
            '9':  0x08,
            '10': 0x09,
            '11': 0x0A,
            '12': 0x0B,
            '13': 0x0C,
            '14': 0x0D,
            '15': 0x0E,
            '16': 0x0F
        }

        if value in ValueStateValues:
            PresetRecallCmdString = pack('>BB', 0xC0, ValueStateValues[value])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
        self.Send(commandstring)

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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