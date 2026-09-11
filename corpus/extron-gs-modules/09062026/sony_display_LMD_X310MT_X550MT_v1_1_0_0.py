from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DMode': {'Parameters': ['Input Connector'], 'Status': {}},
            '3DSignalFormat': {'Parameters': ['Input Connector'], 'Status': {}},
            'AssignPortInputConnector': {'Parameters': ['Port A Input Connector ID', 'Port B Input Connector ID'], 'Status': {}},
            'DetectedSignalStatus': {'Parameters': ['Input Connector'], 'Status': {}},
            'EnergySavingMode': {'Status': {}},
            'FlipPattern': {'Parameters': ['Input Connector'], 'Status': {}},
            'InputPort': {'Status': {}},
            'InputSignal': {'Parameters': ['Port'], 'Status': {}},
            'LoadPresetSetting': {'Status': {}},
            'LoadUserSetting': {'Status': {}},
            'LockMode': {'Status': {}},
            'MultiImageMode': {'Parameters': ['Port'], 'Status': {}},
            'SaveUserSetting': {'Status': {}},
            'SDIInterfaceMode': {'Status': {}},
        }

        self.SetCommandDeliRex = {
            '3DMode': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            '3DSignalFormat': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'AssignPortInputConnector': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'EnergySavingMode': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'FlipPattern': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'InputPort': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'InputSignal': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'LoadPresetSetting': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'LoadUserSetting': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'LockMode': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'MultiImageMode': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'SaveUserSetting': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'SDIInterfaceMode': re.compile(b'(\x02\x01\xBA\x00\x00\x00[\x00-\xFF])|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})')
        }

        self.GetCommandDeliRex = {
            '3DMode': re.compile(b'(\x02\x01\xBA\x00\x00\x04\x90\x50[\x00-\xFF]{3})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            '3DSignalFormat': re.compile(b'(\x02\x01\xBA\x00\x00\x04\x90\x51[\x00-\xFF]{3})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'DetectedSignalStatus': re.compile(b'(\x02\x01\xBA\x00\x00\x13\x80\x08[\x00-\xFF]{18})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'EnergySavingMode': re.compile(b'(\x02\x01\xBA\x00\x00\x03\xF0\x40[\x00-\xFF]{2})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'FlipPattern': re.compile(b'(\x02\x01\xBA\x00\x00\x04\x91\x80[\x00-\xFF]{3})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'InputPort': re.compile(b'(\x02\x01\xBA\x00\x00\x03\x90\x05[\x00-\xFF]{2})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'InputSignal': re.compile(b'(\x02\x01\xBA\x00\x00\x04\x90\x01[\x00-\xFF]{3})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'LockMode': re.compile(b'(\x02\x01\xBA\x00\x00\x03\xF0\x11[\x00-\xFF]{2})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})'),
            'SDIInterfaceMode': re.compile(b'(\x02\x01\xBA\x00\x00\x04\x90\x10[\x00-\xFF]{3})|(\x02\x00\xBA\x00\x00\x02[\x00-\xFF]{3})')
        }

    def calcChkSum(self, cmdstring):
        ChkSum = 0
        for i in range(0, len(cmdstring)):
            ChkSum = ChkSum + cmdstring[i]
        ChkSum = (ChkSum ^ 0xFF) + 1
        ChkSum &= 0xFF
        return ChkSum.to_bytes(1, 'big')

    def Set3DMode(self, value, qualifier):

        InputConnectorStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29,
            'Current': 0xFF
        }

        ValueStateValues = {
            '2D': 0x01,
            '3D to 2D': 0x02,
            '3D': 0x03
        }

        InputConnector = qualifier['Input Connector']
        if InputConnector in InputConnectorStates:
            CmdString = pack('>9B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x10, 0x50, InputConnectorStates[InputConnector], ValueStateValues[value])
            ChkSum = self.calcChkSum(CmdString)
            CmdString = b'\x02' + CmdString + ChkSum
            self.__SetHelper('3DMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set3DMode')

    def Update3DMode(self, value, qualifier):

        InputConnectorStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29,
            'Current': 0xFF
        }

        ValueStateValues = {
            0x01: '2D',
            0x02: '3D to 2D',
            0x03: '3D'
        }

        InputConnector = qualifier['Input Connector']
        if InputConnector in InputConnectorStates:
            CmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x90, 0x50, InputConnectorStates[InputConnector])
            ChkSum = self.calcChkSum(CmdString)
            CmdString = b'\x02' + CmdString + ChkSum
            res = self.__UpdateHelper('3DMode', CmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('3DMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['3D Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for Update3DMode')

    def Set3DSignalFormat(self, value, qualifier):

        InputConnectorStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29
        }

        ValueStateValues = {
            'Dual Stream': 0x01,
            'Side by Side': 0x02,
            'Top and Bottom': 0x03,
            'Line by Line': 0x04,
            'Auto': 0x10
        }

        InputConnector = qualifier['Input Connector']
        if InputConnector in InputConnectorStates:
            SignalFormatCmdString = pack('>9B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x10, 0x51, InputConnectorStates[InputConnector], ValueStateValues[value])
            ChkSum = self.calcChkSum(SignalFormatCmdString)
            SignalFormatCmdString = b'\x02' + SignalFormatCmdString + ChkSum
            self.__SetHelper('3DSignalFormat', SignalFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set3DSignalFormat')

    def Update3DSignalFormat(self, value, qualifier):

        InputConnectorStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29
        }

        ValueStateValues = {
            0x01: 'Dual Stream',
            0x02: 'Side by Side',
            0x03: 'Top and Bottom',
            0x04: 'Line by Line',
            0x10: 'Auto'
        }

        InputConnector = qualifier['Input Connector']
        if InputConnector in InputConnectorStates:
            SignalFormatCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x90, 0x51, InputConnectorStates[InputConnector])
            ChkSum = self.calcChkSum(SignalFormatCmdString)
            SignalFormatCmdString = b'\x02' + SignalFormatCmdString + ChkSum
            res = self.__UpdateHelper('3DSignalFormat', SignalFormatCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('3DSignalFormat', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['3D Signal Format: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for Update3DSignalFormat')

    def SetAssignPortInputConnector(self, value, qualifier):

        PortAInputConnectorIDStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29,
            'Common': 0x00,
            'Present': 0xFF
        }

        PortBInputConnectorIDStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29,
            'Common': 0x00,
            'Present': 0xFF
        }

        value1 = qualifier['Port A Input Connector ID']
        value2 = qualifier['Port B Input Connector ID']
        if value1 in PortAInputConnectorIDStates and value2 in PortBInputConnectorIDStates:
            AssignPortInputConnectorCmdString = pack('>11B', 0x00, 0xBA, 0x00, 0x00, 0x06, 0x10, 0x04, 0x01, PortAInputConnectorIDStates[value1], 0x02, PortBInputConnectorIDStates[value2])
            ChkSum = self.calcChkSum(AssignPortInputConnectorCmdString)
            AssignPortInputConnectorCmdString = b'\x02' + AssignPortInputConnectorCmdString + ChkSum
            self.__SetHelper('AssignPortInputConnector', AssignPortInputConnectorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAssignPortInputConnector')

    def UpdateDetectedSignalStatus(self, value, qualifier):

        InputConnectorStates = {
            'SDI 1 - A': [0x01, 0x01],
            'SDI 1 - B': [0x01, 0x02],
            'SDI 1 - C': [0x01, 0x03],
            'SDI 1 - D': [0x01, 0x04],
            'SDI 2': [0x02, 0x00],
            'DVI-D': [0x11, 0x00],
            'HDMI': [0x29, 0x00]
        }

        ValueStateValues = {
            0x01: 'Signal is not supported',
            0x7E: 'Signal is suspended',
            0x80: 'No Sync',
            0x81: 'Unknown',
            0x82: 'Out of Range'
        }

        InputConnector = qualifier['Input Connector']
        if InputConnector in InputConnectorStates:
            DetectedSignalStatusCmdString = pack('>10B', 0x00, 0xBA, 0x00, 0x00, 0x05, 0x80, 0x08, 0x02, InputConnectorStates[InputConnector][0], InputConnectorStates[InputConnector][1])
            ChkSum = self.calcChkSum(DetectedSignalStatusCmdString)
            DetectedSignalStatusCmdString = b'\x02' + DetectedSignalStatusCmdString + ChkSum
            res = self.__UpdateHelper('DetectedSignalStatus', DetectedSignalStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[10]]
                    self.WriteStatus('DetectedSignalStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Detected Signal Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDetectedSignalStatus')

    def SetEnergySavingMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        EnergySavingModeCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x70, 0x41, ValueStateValues[value])
        ChkSum = self.calcChkSum(EnergySavingModeCmdString)
        EnergySavingModeCmdString = b'\x02' + EnergySavingModeCmdString + ChkSum
        self.__SetHelper('EnergySavingMode', EnergySavingModeCmdString, value, qualifier)

    def UpdateEnergySavingMode(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        EnergySavingModeCmdString = pack('>7B', 0x00, 0xBA, 0x00, 0x00, 0x02, 0xF0, 0x41)
        ChkSum = self.calcChkSum(EnergySavingModeCmdString)
        EnergySavingModeCmdString = b'\x02' + EnergySavingModeCmdString + ChkSum
        res = self.__UpdateHelper('EnergySavingMode', EnergySavingModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('EnergySavingMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Energy Saving Mode: Invalid/unexpected response'])

    def SetFlipPattern(self, value, qualifier):

        InputConnectorStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29
        }

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x01
        }

        InputConnector = qualifier['Input Connector']
        if InputConnector in InputConnectorStates:
            FlipPatternCmdString = pack('>9B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x11, 0x80, InputConnectorStates[InputConnector], ValueStateValues[value])
            ChkSum = self.calcChkSum(FlipPatternCmdString)
            FlipPatternCmdString = b'\x02' + FlipPatternCmdString + ChkSum
            self.__SetHelper('FlipPattern', FlipPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlipPattern')

    def UpdateFlipPattern(self, value, qualifier):

        InputConnectorStates = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29
        }

        ValueStateValues = {
            0x02: 'On',
            0x01: 'Off'
        }

        InputConnector = qualifier['Input Connector']
        if InputConnector in InputConnectorStates:
            FlipPatternCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x91, 0x80, InputConnectorStates[InputConnector])
            ChkSum = self.calcChkSum(FlipPatternCmdString)
            FlipPatternCmdString = b'\x02' + FlipPatternCmdString + ChkSum
            res = self.__UpdateHelper('FlipPattern', FlipPatternCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('FlipPattern', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Flip Pattern: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFlipPattern')

    def SetInputPort(self, value, qualifier):

        ValueStateValues = {
            'Port A': 0x01,
            'Port B': 0x02
        }

        InputPortCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x10, 0x05, ValueStateValues[value])
        ChkSum = self.calcChkSum(InputPortCmdString)
        InputPortCmdString = b'\x02' + InputPortCmdString + ChkSum
        self.__SetHelper('InputPort', InputPortCmdString, value, qualifier)

    def UpdateInputPort(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Port A',
            0x02: 'Port B'
        }

        InputPortCmdString = pack('>7B', 0x00, 0xBA, 0x00, 0x00, 0x02, 0x90, 0x05)
        ChkSum = self.calcChkSum(InputPortCmdString)
        InputPortCmdString = b'\x02' + InputPortCmdString + ChkSum
        res = self.__UpdateHelper('InputPort', InputPortCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('InputPort', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input Port: Invalid/unexpected response'])

    def SetInputSignal(self, value, qualifier):

        PortStates = {
            'Port A': 0x01,
            'Port B': 0x02
        }

        ValueStateValues = {
            'SDI 1': 0x01,
            'SDI 2': 0x02,
            'DVI-D': 0x11,
            'HDMI': 0x29
        }

        port = qualifier['Port']
        if port in PortStates:
            InputSignalCmdString = pack('>9B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x10, 0x01, PortStates[port], ValueStateValues[value])
            ChkSum = self.calcChkSum(InputSignalCmdString)
            InputSignalCmdString = b'\x02' + InputSignalCmdString + ChkSum
            self.__SetHelper('InputSignal', InputSignalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSignal')

    def UpdateInputSignal(self, value, qualifier):

        PortStates = {
            'Port A': 0x01,
            'Port B': 0x02
        }

        ValueStateValues = {
            0x01: 'SDI 1',
            0x02: 'SDI 2',
            0x11: 'DVI-D',
            0x29: 'HDMI'
        }

        port = qualifier['Port']
        if port in PortStates:
            InputSignalCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x90, 0x01, PortStates[port])
            ChkSum = self.calcChkSum(InputSignalCmdString)
            InputSignalCmdString = b'\x02' + InputSignalCmdString + ChkSum
            res = self.__UpdateHelper('InputSignal', InputSignalCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('InputSignal', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Signal: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputSignal')

    def SetLoadPresetSetting(self, value, qualifier):

        ValueStateValues = {
            'Preset A': 0x01,
            'Preset B': 0x02,
            'Preset C': 0x03,
            'Preset D': 0x04,
            'Preset E': 0x05,
            'Preset F': 0x06,
            'Preset G': 0x07,
            'Preset H': 0x08,
            'Preset I': 0x09,
            'Preset J': 0x0A,
            'Preset K': 0x0B,
            'Preset L': 0x0C,
            'Preset M': 0x0D,
            'Preset N': 0x0E,
            'Preset O': 0x0F,
            'Preset P': 0x10,
            'Preset Q': 0x11,
            'Preset R': 0x12,
            'Preset S': 0x13,
            'Preset T': 0x14
        }

        LoadPresetSettingCmdString = pack('>9B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x20, 0x20, 0xFF, ValueStateValues[value])
        ChkSum = self.calcChkSum(LoadPresetSettingCmdString)
        LoadPresetSettingCmdString = b'\x02' + LoadPresetSettingCmdString + ChkSum
        self.__SetHelper('LoadPresetSetting', LoadPresetSettingCmdString, value, qualifier)

    def SetLoadUserSetting(self, value, qualifier):

        ValueStateValues = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10,
            '17': 0x11,
            '18': 0x12,
            '19': 0x13,
            '20': 0x14
        }

        LoadUserSettingCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x20, 0x01, ValueStateValues[value])
        ChkSum = self.calcChkSum(LoadUserSettingCmdString)
        LoadUserSettingCmdString = b'\x02' + LoadUserSettingCmdString + ChkSum
        self.__SetHelper('LoadUserSetting', LoadUserSettingCmdString, value, qualifier)

    def SetLockMode(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x01,
            'Menu & Button': 0x02
        }

        LockModeCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x70, 0x11, ValueStateValues[value])
        ChkSum = self.calcChkSum(LockModeCmdString)
        LockModeCmdString = b'\x02' + LockModeCmdString + ChkSum
        self.__SetHelper('LockMode', LockModeCmdString, value, qualifier)

    def UpdateLockMode(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Menu',
            0x02: 'Menu & Button'
        }

        LockModeCmdString = pack('>7B', 0x00, 0xBA, 0x00, 0x00, 0x02, 0xF0, 0x11)
        ChkSum = self.calcChkSum(LockModeCmdString)
        LockModeCmdString = b'\x02' + LockModeCmdString + ChkSum
        res = self.__UpdateHelper('LockMode', LockModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('LockMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lock Mode: Invalid/unexpected response'])

    def SetMultiImageMode(self, value, qualifier):

        PortStates = {
            'Port A': 0x01,
            'Port B': 0x02
        }

        ValueStateValues = {
            'Single Display': 0x01,
            'Multi-Image/PIP1': 0x11,
            'Multi-Image/PIP2': 0x12,
            'Multi-Image/POP1': 0x21,
            'Multi-Image/POP2': 0x22
        }

        port = qualifier['Port']
        if port in PortStates:
            MultiImageModeCmdString = pack('>9B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x10, 0x20, ValueStateValues[value], PortStates[port])
            ChkSum = self.calcChkSum(MultiImageModeCmdString)
            MultiImageModeCmdString = b'\x02' + MultiImageModeCmdString + ChkSum
            self.__SetHelper('MultiImageMode', MultiImageModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiImageMode')

    def SetSaveUserSetting(self, value, qualifier):

        ValueStateValues = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10,
            '17': 0x11,
            '18': 0x12,
            '19': 0x13,
            '20': 0x14
        }

        LoadUserSettingCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x03, 0x20, 0x01, ValueStateValues[value])
        ChkSum = self.calcChkSum(LoadUserSettingCmdString)
        LoadUserSettingCmdString = b'\x02' + LoadUserSettingCmdString + ChkSum
        self.__SetHelper('LoadUserSetting', LoadUserSettingCmdString, value, qualifier)

    def SetSDIInterfaceMode(self, value, qualifier):

        ValueStateValues = {
            '4K Quad': 0x01,
            '4K Dual': 0x02,
            'HD Dual': 0x10,
            'HD/SD Single': 0x11,
            'HD/SD Quad View': 0x20
        }

        SDIInterfaceModeCmdString = pack('>9B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x10, 0x10, 0x01, ValueStateValues[value])
        ChkSum = self.calcChkSum(SDIInterfaceModeCmdString)
        SDIInterfaceModeCmdString = b'\x02' + SDIInterfaceModeCmdString + ChkSum
        self.__SetHelper('SDIInterfaceMode', SDIInterfaceModeCmdString, value, qualifier)

    def UpdateSDIInterfaceMode(self, value, qualifier):

        ValueStateValues = {
            0x01: '4K Quad',
            0x02: '4K Dual',
            0x10: 'HD Dual',
            0x11: 'HD/SD Single',
            0x20: 'HD/SD Quad View'
        }

        SDIInterfaceModeCmdString = pack('>8B', 0x00, 0xBA, 0x00, 0x00, 0x04, 0x90, 0x10, 0x01)
        ChkSum = self.calcChkSum(SDIInterfaceModeCmdString)
        SDIInterfaceModeCmdString = b'\x02' + SDIInterfaceModeCmdString + ChkSum
        res = self.__UpdateHelper('SDIInterfaceMode', SDIInterfaceModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('SDIInterfaceMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['SDI Interface Mode: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01\x01': 'Invalid Item',
            b'\x01\x02': 'Invalid Item Request',
            b'\x01\x03': 'Invalid Length',
            b'\x01\x04': 'Invalid Data',
            b'\x01\x11': 'Short Data',
            b'\x01\x20': 'Invalid Sub Command',
            b'\x01\x21': 'Invalid Sub Command Data',
            b'\x01\x2E': 'Not Execute When Force Sleep',
            b'\x01\x2F': 'Need Initial Settings',
            b'\x01\x30': 'System is starting up',
            b'\x01\x31': 'Initial Settings are executed already',
            b'\x01\x90': 'Not Executed Order or Setting',
            b'\x01\x91': 'Unexpected Error',
            b'\x01\x92': 'Not Read Value',
            b'\xF0\x10': 'Check Sum Error',
            b'\xF0\xF0': 'Unknown Response'
        }

        if response[0:6] == b'\x02\x00\xBA\x00\x00\x02':
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[-3:-1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command in 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetCommandDeliRex[command])
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.GetCommandDeliRex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except BaseException:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    return None
        try:
            return Status['Live']
        except BaseException:
            return None


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
