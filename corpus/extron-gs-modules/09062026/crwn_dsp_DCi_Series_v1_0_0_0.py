from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {
            'DCi 2|300N': self.crwn_25_3156_2,
            'DCi 2|600N': self.crwn_25_3156_2,
            'DCi 2|1250N': self.crwn_25_3156_2,
            'DCi 2|2400N': self.crwn_25_3156_2,
            'DCi 4|300N': self.crwn_25_3156_4,
            'DCi 4|600N': self.crwn_25_3156_4,
            'DCi 4|1250N': self.crwn_25_3156_4,
            'DCi 4|2400N': self.crwn_25_3156_4,
            'DCi 8|300N': self.crwn_25_3156_8,
            'DCi 8|600N': self.crwn_25_3156_8,
        }

        self.Commands = {
            'AnalogInputFader': {'Parameters': ['Channel'], 'Status': {}},
            'AnalogInputMute': {'Parameters': ['Channel'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'ProcessingOutputFader': {'Parameters': ['Channel'], 'Status': {}},
            'ProcessingOutputMute': {'Parameters': ['Channel'], 'Status': {}},
        }

        self._DeviceID = 1
        self._SourceAddress = 1
        self.Command_Header = pack('>15B', 0x02, 0x19, 0x00, 0x00, 0x00, 0x1F, 0x00, self._DeviceID, 0x00, 0x00, 0x00, 0x00, 0x00, self._SourceAddress, 0x00)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 255:
            self._DeviceID = int(value)
            self.Command_Header = pack('>15B', 0x02, 0x19, 0x00, 0x00, 0x00, 0x1F, 0x00, self._DeviceID, 0x00, 0x00, 0x00, 0x00, 0x00, self._SourceAddress, 0x00)
    @property
    def SourceAddress(self):
        return self._SourceAddress

    @SourceAddress.setter
    def SourceAddress(self, value):
        if 1 <= int(value) <= 255:
            self._SourceAddress = int(value)
            self.Command_Header = pack('>15B', 0x02, 0x19, 0x00, 0x00, 0x00, 0x1F, 0x00, self._DeviceID, 0x00, 0x00, 0x00, 0x00, 0x00, self._SourceAddress, 0x00)

    def SetAnalogInputFader(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }
        channel = int(qualifier['Channel'])
        conv_value = int((value + 100) * 2)
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= self.max_channel:
            AnalogInputFaderCmdString = self.Command_Header + pack('>16B', 0x01, 0x08, channel, 0x01, 0x00, 0x00, 0x20, 0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x03, 0x01, conv_value)
            self.__SetHelper('AnalogInputFader', AnalogInputFaderCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputFader')

    def SetAnalogInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }
        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.max_channel:
            AnalogInputMuteCmdString = self.Command_Header + pack('>16B', 0x01, 0x08, channel, 0x01, 0x00, 0x00, 0x20, 0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x05, 0x01, ValueStateValues[value])
            self.__SetHelper('AnalogInputMute', AnalogInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputMute')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 20:
            PresetRecallCmdString = self.Command_Header + pack('>16B', 0x15, 0x04, 0x00, 0x01, 0x00, 0x00, 0x20, 0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x04, 0x01, int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 20:
            PresetSaveCmdString = self.Command_Header + pack('>16B', 0x15, 0x04, 0x00, 0x01, 0x00, 0x00, 0x20, 0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x01, int(value))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetProcessingOutputFader(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        channel = int(qualifier['Channel'])
        conv_value = int((value + 100) * 2)
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= self.max_channel:
            ProcessingOutputFaderCmdString = self.Command_Header + pack('>16B', 0x0F, 0x16, channel, 0x01, 0x00, 0x00, 0x20, 0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x03, 0x01, conv_value)
            self.__SetHelper('ProcessingOutputFader', ProcessingOutputFaderCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProcessingOutputFader')

    def SetProcessingOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.max_channel:
            ProcessingOutputMuteCmdString = self.Command_Header + pack('>16B', 0x0F, 0x16, channel, 0x01, 0x00, 0x00, 0x20, 0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x06, 0x01, ValueStateValues[value])
            self.__SetHelper('ProcessingOutputMute', ProcessingOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProcessingOutputMute')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def crwn_25_3156_8(self):
        self.max_channel = 8

    def crwn_25_3156_4(self):
        self.max_channel = 4

    def crwn_25_3156_2(self):
        self.max_channel = 2

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
