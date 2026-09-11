from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {
            'DH48E': self.smsg_10_1761_1,
            'DH55E': self.smsg_10_1761_1,
            'DM40E': self.smsg_10_1761_2,
            'DB32E': self.smsg_10_1761_0,
            'DB40E': self.smsg_10_1761_0,
            'DB48E': self.smsg_10_1761_0,
            'DH40E': self.smsg_10_1761_1,
            'DB55E': self.smsg_10_1761_0,
            'DM32E': self.smsg_10_1761_0,
            'DM48E': self.smsg_10_1761_2,
            'DM55E': self.smsg_10_1761_2,
            'DM65E': self.smsg_10_1761_2,
            'DM75E': self.smsg_10_1761_2,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'IRControl': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'Panel': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWall': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallMode': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallSize': {'Parameters': ['Device ID', 'Row', 'Column'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x18([\x01\x04\x31\x0B])[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x13([\x00\x01])[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x5D([\x01\x00])[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x14([\x14\x18\x0C\x08\x20\x1F\x30\x40\x21\x22\x23\x24\x25\x60\x61])[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x36([\x00\x01])[\x00-\xFF]'), self.__MatchIRControl, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\xF9([\x01\x00])[\x00-\xFF]'), self.__MatchPanel, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x3C([\x01\x00])[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x11([\x01\x00])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x84([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\\x5C([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x04\x41\x89(?P<size>[\x00-\xFF])(?P<value>[\x00-\x64])(?P<checksum>[\x00-\xFF])'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x4E([\x11\x12\x13\x14\x18\x36\x3C\x5C\x5D\x84\x89\x3D\xB0])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    def GetDeviceID(self, ID):

        if ID == 'Broadcast':
            return 254
        elif 0 <= int(ID) <= 224:
            return int(ID)
        else:
            return None

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': 0x01,
            'Zoom': 0x04,
            'Wide Zoom': 0x31,
            '4:3': 0x0B
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x18 + ID + 0x01 + ValueStateValues[value]) & 0xFF
            AspectRatioCmdString = pack('>BBBBBB', 0xAA, 0x18, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x18 + ID) & 0xFF
            AspectRatioCmdString = pack('>BBBBB', 0xAA, 0x18, ID, 0x00, checksum)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x01': '16:9',
            b'\x04': 'Zoom',
            b'\x31': 'Wide Zoom',
            b'\x0B': '4:3'
        }

        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x13 + ID + 0x01 + ValueStateValues[value]) & 0xFF
            AudioMuteCmdString = pack('>BBBBBB', 0xAA, 0x13, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x13 + ID) & 0xFF
            AudioMuteCmdString = pack('>BBBBB', 0xAA, 0x13, ID, 0x00, checksum)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'On'
        }

        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x3D + ID + 0x01) & 0xFF
            AutoImageCmdString = pack('>BBBBBB', 0xAA, 0x3D, ID, 0x01, 0x00, checksum)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x5D + ID + 0x01 + ValueStateValues[value]) & 0xFF
            ExecutiveModeCmdString = pack('>BBBBBB', 0xAA, 0x5D, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x5D + ID) & 0xFF
            ExecutiveModeCmdString = pack('>BBBBB', 0xAA, 0x5D, ID, 0x00, checksum)
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x14 + ID + 0x01 + self.ValueState[value]) & 0xFF
            InputCmdString = pack('>BBBBBB', 0xAA, 0x14, ID, 0x01, self.ValueState[value], checksum)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x14 + ID) & 0xFF
            InputCmdString = pack('>BBBBB', 0xAA, 0x14, ID, 0x00, checksum)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        try:
            qualifier = {'Device ID': str(ord(match.group(1)))}
            value = self.ValueValues[match.group(2)]
            self.WriteStatus('Input', value, qualifier)
        except(KeyError, IndexError):
            self.Error(['Input: Invalid/unexpected response'])

    def SetIRControl(self, value, qualifier):

        ValueStateValues = {
            'Enable IR': 0x01,
            'Disable IR': 0x00
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x36 + ID + 0x01 + ValueStateValues[value]) & 0xFF
            IRControlCmdString = pack('>BBBBBB', 0xAA, 0x36, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('IRControl', IRControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRControl')

    def UpdateIRControl(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x36 + ID) & 0xFF
            IRControlCmdString = pack('>BBBBB', 0xAA, 0x36, ID, 0x00, checksum)
            self.__UpdateHelper('IRControl', IRControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateIRControl')

    def __MatchIRControl(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Enable IR',
            b'\x00': 'Disable IR'
        }

        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('IRControl', value, qualifier)

    def SetPanel(self, value, qualifier):

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x01
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0xF9 + ID + 0x01 + ValueStateValues[value]) & 0xFF
            PanelCmdString = pack('>BBBBBB', 0xAA, 0xF9, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('Panel', PanelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanel')

    def UpdatePanel(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0xF9 + ID) & 0xFF
            PanelCmdString = pack('>BBBBB', 0xAA, 0xF9, ID, 0x00, checksum)
            self.__UpdateHelper('Panel', PanelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePanel')

    def __MatchPanel(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Panel', value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x3C + ID + 0x01 + ValueStateValues[value]) & 0xFF
            PIPModeCmdString = pack('>BBBBBB', 0xAA, 0x3C, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x3C + ID) & 0xFF
            PIPModeCmdString = pack('>BBBBB', 0xAA, 0x3C, ID, 0x00, checksum)
            self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPMode')

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('PIPMode', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x11 + ID + 0x01 + ValueStateValues[value]) & 0xFF
            PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x11 + ID) & 0xFF
            PowerCmdString = pack('>BBBBB', 0xAA, 0x11, ID, 0x00, checksum)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Power', value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x1A,
            'Up': 0x60,
            'Down': 0x61,
            'Left': 0x65,
            'Right': 0x62,
            'Enter': 0x68,
            'Return': 0x58,
            'Exit': 0x2D
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0xB0 + ID + 0x01 + ValueStateValues[value]) & 0xFF
            MenuNavigationCmdString = pack('>BBBBBB', 0xAA, 0xB0, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetVideoWall(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        if ID is not None:
            checksum = (0x84 + ID + 0x01 + ValueStateValues[value]) & 0xFF
            VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWall')

    def UpdateVideoWall(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x84 + ID) & 0xFF
            VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, ID, 0x00, checksum)
            self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWall')

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('VideoWall', value, qualifier)

    def SetVideoWallMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        ValueStateValues = {
            'Full': 0x01,
            'Natural': 0x00
        }

        if ID is not None:
            checksum = (0x5C + ID + 0x01 + ValueStateValues[value]) & 0xFF
            VideoWallModeCmdString = pack('>BBBBBB', 0xAA, 0x5C, ID, 0x01, ValueStateValues[value], checksum)
            self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallMode')

    def UpdateVideoWallMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x5C + ID) & 0xFF
            VideoWallModeCmdString = pack('>BBBBB', 0xAA, 0x5C, ID, 0x00, checksum)
            self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWallMode')

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Full',
            b'\x00': 'Natural'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('VideoWallMode', value, qualifier)

    def SetVideoWallSize(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        RowStates = {
            '1': 0x10,
            '2': 0x20,
            '3': 0x30,
            '4': 0x40,
            '5': 0x50,
            '6': 0x60,
            '7': 0x70,
            '8': 0x80,
            '9': 0x90,
            '10': 0xA0,
            '11': 0xB0,
            '12': 0xC0,
            '13': 0xD0,
            '14': 0xE0,
            '15': 0xF0,
        }

        row = RowStates[qualifier['Row']]
        column = int(qualifier['Column'])
        displayNum = int(value)

        if ID is not None and 0 < column <= 15 and 0 < displayNum <= 100:
            size = row + column
            if row <= 0x60 and column <= 15 and displayNum <= 90:
                Valid = True
            elif row <= 0x70 and column < 15 and displayNum <= 98:
                Valid = True
            elif row <= 0x80 and column < 13 and displayNum <= 96:
                Valid = True
            elif row <= 0x90 and column < 12 and displayNum <= 99:
                Valid = True
            elif row <= 0xA0 and column < 11:
                Valid = True
            elif row <= 0xB0 and column < 10 and displayNum <= 99:
                Valid = True
            elif row <= 0xC0 and column < 9 and displayNum <= 96:
                Valid = True
            elif row <= 0xD0 and column < 8 and displayNum <= 91:
                Valid = True
            elif row <= 0xE0 and column < 8 and displayNum <= 98:
                Valid = True
            elif row <= 0xF0 and column < 7 and displayNum <= 90:
                Valid = True
            else:
                Valid = False

            if Valid:
                checksum = (0x89 + ID + 0x02 + size + displayNum) & 0xFF
                VideoWallSizeCmdString = pack('>BBBBBBB', 0xAA, 0x89, ID, 0x02, size, displayNum, checksum)
                self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x89 + ID) & 0xFF
            VideoWallSizeCmdString = pack('>BBBBB', 0xAA, 0x89, ID, 0x00, checksum)
            self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWallSize')

    def __MatchVideoWallSize(self, match, tag):

        value = str(ord(match.group('value')))  # Display Num - Value
        value2 = ord(match.group('size'))
        if value2 < 0x20:  # row 1
            row = '1'
            value3 = value2 - 0x10
        elif value2 < 0x30:  # row 2
            row = '2'
            value3 = value2 - 0x20
        elif value2 < 0x40:  # row 3
            row = '3'
            value3 = value2 - 0x30
        elif value2 < 0x50:  # row 4
            row = '4'
            value3 = value2 - 0x40
        elif value2 < 0x60:  # row 5
            row = '5'
            value3 = value2 - 0x50
        elif value2 < 0x70:  # row 6
            row = '6'
            value3 = value2 - 0x60
        elif value2 < 0x80:  # row 7
            row = '7'
            value3 = value2 - 0x70
        elif value2 < 0x90:  # row 8
            row = '8'
            value3 = value2 - 0x80
        elif value2 < 0xA0:  # row 9
            row = '9'
            value3 = value2 - 0x90
        elif value2 < 0xB0:  # row 10
            row = '10'
            value3 = value2 - 0xA0
        elif value2 < 0xC0:  # row 11
            row = '11'
            value3 = value2 - 0xB0
        elif value2 < 0xD0:  # row 12
            row = '12'
            value3 = value2 - 0xC0
        elif value2 < 0xE0:  # row 13
            row = '13'
            value3 = value2 - 0xD0
        elif value2 < 0xF0:  # row 14
            row = '14'
            value3 = value2 - 0xE0
        elif value2 < 0xF7:  # row 15
            row = '15'
            value3 = value2 - 0xF0

        qualifier = {
            'Column': str(value3),
            'Row': row,
            'Device ID': str(ord(match.group(1)))
        }

        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None and 0 <= value <= 100:
            checksum = (0x12 + ID + 0x01 + value) & 0xFF
            VolumeCmdString = pack('>BBBBBB', 0xAA, 0x12, ID, 0x01, value, checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID is not None:
            checksum = (0x12 + ID) & 0xFF
            VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, ID, 0x00, checksum)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ord(match.group(2).decode())
        self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        Reject = False
        if 'Device ID' in qualifier and qualifier['Device ID'] == 'Broadcast':
            Reject = True

        if self.Unidirectional == 'True' or Reject:
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        Error = {
            b'\x11': 'Power',
            b'\x12': 'Volume',
            b'\x13': 'AudioMute',
            b'\x14': 'Input',
            b'\x18': 'AspectRatio',
            b'\x36': 'IRControl',
            b'\x3C': 'PIPMode',
            b'\x5C': 'VideoWallMode',
            b'\x5D': 'ExecutiveMode',
            b'\x84': 'VideoWall',
            b'\x89': 'VideoWallSize',
            b'\x3D': 'AutoImage',
            b'\xB0': 'MenuNavigation'
        }
        self.Error(['Device ID: {0}, Command: {1}, Error Code: {2}'.format(match.group(1)[0], Error[match.group(2)], match.group(3)[0])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_10_1761_0(self):

        self.ValueState = {
            'PC': 0x14,
            'DVI': 0x18,
            'MagicInfo': 0x20,
            'AV': 0x0C,
            'DTV': 0x40,
            'RF (TV)': 0x30,
            'HDMI': 0x21,
            'MagicInfo Lite': 0x60,
            'WiDi/Screen Mirroring': 0x61
        }

        self.ValueValues = {
            b'\x14': 'PC',
            b'\x18': 'DVI',
            b'\x20': 'MagicInfo',
            b'\x0C': 'AV',
            b'\x40': 'DTV',
            b'\x1F': 'DVI - VIDEO',
            b'\x22': 'HDMI 1 PC',
            b'\x21': 'HDMI',
            b'\x30': 'RF (TV)',
            b'\x60': 'MagicInfo Lite',
            b'\x61': 'WiDi/Screen Mirroring'
        }

    def smsg_10_1761_1(self):

        self.ValueState = {
            'PC': 0x14,
            'DVI': 0x18,
            'MagicInfo': 0x20,
            'AV': 0x0C,
            'DTV': 0x40,
            'DisplayPort': 0x25,
            'HDMI': 0x21,
            'RF (TV)': 0x30,
            'MagicInfo Lite': 0x60,
            'WiDi/Screen Mirroring': 0x61
        }

        self.ValueValues = {
            b'\x14': 'PC',
            b'\x18': 'DVI',
            b'\x20': 'MagicInfo',
            b'\x0C': 'AV',
            b'\x40': 'DTV',
            b'\x25': 'DisplayPort',
            b'\x1F': 'DVI - VIDEO',
            b'\x22': 'HDMI 1 PC',
            b'\x21': 'HDMI',
            b'\x30': 'RF (TV)',
            b'\x60': 'MagicInfo Lite',
            b'\x61': 'WiDi/Screen Mirroring'
        }

    def smsg_10_1761_2(self):

        self.ValueState = {
            'PC': 0x14,
            'DVI': 0x18,
            'MagicInfo': 0x20,
            'AV': 0x0C,
            'DTV': 0x40,
            'DisplayPort': 0x25,
            'HDMI 1': 0x21,
            'HDMI 2': 0x23,
            'RF (TV)': 0x30,
            'MagicInfo Lite': 0x60,
            'WiDi/Screen Mirroring': 0x61
        }

        self.ValueValues = {
            b'\x14': 'PC',
            b'\x18': 'DVI',
            b'\x20': 'MagicInfo',
            b'\x0C': 'AV',
            b'\x40': 'DTV',
            b'\x25': 'DisplayPort',
            b'\x1F': 'DVI - VIDEO',
            b'\x22': 'HDMI 1 PC',
            b'\x24': 'HDMI 2 PC',
            b'\x21': 'HDMI 1',
            b'\x23': 'HDMI 2',
            b'\x30': 'RF (TV)',
            b'\x60': 'MagicInfo Lite',
            b'\x61': 'WiDi/Screen Mirroring'
        }

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
                    except:
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
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands.get(command, None)
        if Command:
            Status = Command['Status']
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Status = Status[qualifier[Parameter]]
                    except KeyError:
                        return None
            try:
                return Status['Live']
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {
            'DM32E': self.smsg_10_1761_0,
            'DM48E': self.smsg_10_1761_2,
            'DM55E': self.smsg_10_1761_2,
            'DB55E': self.smsg_10_1761_0,
            'DM65E': self.smsg_10_1761_2,
            'DM75E': self.smsg_10_1761_2,
            'DB32E': self.smsg_10_1761_0,
            'DB40E': self.smsg_10_1761_0,
            'DB48E': self.smsg_10_1761_0,
            'DH40E': self.smsg_10_1761_1,
            'DH48E': self.smsg_10_1761_1,
            'DH55E': self.smsg_10_1761_1,
            'DM40E': self.smsg_10_1761_2,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'IRControl': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Panel': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'VideoWallSize': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x18([\x01\x04\x31\x0B])[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13([\x00\x01])[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D([\x01\x00])[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14([\x14\x18\x0C\x08\x20\x1F\x30\x40\x21\x22\x23\x24\x25\x60\x61])[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x36([\x00\x01])[\x00-\xFF]'), self.__MatchIRControl, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\xF9([\x01\x00])[\x00-\xFF]'), self.__MatchPanel, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C([\x01\x00])[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11([\x01\x00])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF(?P<DeviceID>[\x00-\xFF])\x04\x41\x89(?P<size>[\x00-\xFF])(?P<value>[\x00-\x64])(?P<checksum>[\x00-\xFF])'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x4E([\x11\x12\x13\x14\x18\x36\x3C\x5C\x5D\x84\x89\x3D\xB0])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 254
        elif 0 <= int(value) <= 224:
            self._DeviceID = int(value)
        else:
            self.Error(['DeviceID should be a value between 0 to 224 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': 0x01,
            'Zoom': 0x04,
            'Wide Zoom': 0x31,
            '4:3': 0x0B
        }

        checksum = (0x18 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        AspectRatioCmdString = pack('>BBBBBB', 0xAA, 0x18, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        checksum = (0x18 + self._DeviceID) & 0xFF
        AspectRatioCmdString = pack('>BBBBB', 0xAA, 0x18, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x01': '16:9',
            b'\x04': 'Zoom',
            b'\x31': 'Wide Zoom',
            b'\x0B': '4:3'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = (0x13 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        AudioMuteCmdString = pack('>BBBBBB', 0xAA, 0x13, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        checksum = (0x13 + self._DeviceID) & 0xFF
        AudioMuteCmdString = pack('>BBBBB', 0xAA, 0x13, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'On'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        checksum = (0x3D + self._DeviceID + 0x01) & 0xFF
        AutoImageCmdString = pack('>BBBBBB', 0xAA, 0x3D, self._DeviceID, 0x01, 0x00, checksum)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = (0x5D + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        ExecutiveModeCmdString = pack('>BBBBBB', 0xAA, 0x5D, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        checksum = (0x5D + self._DeviceID) & 0xFF
        ExecutiveModeCmdString = pack('>BBBBB', 0xAA, 0x5D, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        checksum = (0x14 + self._DeviceID + 0x01 + self.ValueState[value]) & 0xFF
        InputCmdString = pack('>BBBBBB', 0xAA, 0x14, self._DeviceID, 0x01, self.ValueState[value], checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        checksum = (0x14 + self._DeviceID) & 0xFF
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        try:
            value = self.ValueValues[match.group(1)]
            self.WriteStatus('Input', value, None)
        except KeyError:
            self.Error(['Input: Invalid/unexpected response'])

    def SetIRControl(self, value, qualifier):

        ValueStateValues = {
            'Enable IR': 0x01,
            'Disable IR': 0x00
        }
        checksum = (0x36 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        IRControlCmdString = pack('>BBBBBB', 0xAA, 0x36, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('IRControl', IRControlCmdString, value, qualifier)

    def UpdateIRControl(self, value, qualifier):

        checksum = (0x36 + self._DeviceID) & 0xFF
        IRControlCmdString = pack('>BBBBB', 0xAA, 0x36, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('IRControl', IRControlCmdString, value, qualifier)

    def __MatchIRControl(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Enable IR',
            b'\x00': 'Disable IR'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('IRControl', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x1A,
            'Up': 0x60,
            'Down': 0x61,
            'Left': 0x65,
            'Right': 0x62,
            'Enter': 0x68,
            'Return': 0x58,
            'Exit': 0x2D
        }

        checksum = (0xB0 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        MenuNavigationCmdString = pack('>BBBBBB', 0xAA, 0xB0, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPanel(self, value, qualifier):

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x01
        }

        checksum = (0xF9 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        PanelCmdString = pack('>BBBBBB', 0xAA, 0xF9, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('Panel', PanelCmdString, value, qualifier)

    def UpdatePanel(self, value, qualifier):

        checksum = (0xF9 + self._DeviceID) & 0xFF
        PanelCmdString = pack('>BBBBB', 0xAA, 0xF9, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Panel', PanelCmdString, value, qualifier)

    def __MatchPanel(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Panel', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = (0x3C + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        PIPModeCmdString = pack('>BBBBBB', 0xAA, 0x3C, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        checksum = (0x3C + self._DeviceID) & 0xFF
        PIPModeCmdString = pack('>BBBBB', 0xAA, 0x3C, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = (0x11 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        checksum = (0x11 + self._DeviceID) & 0xFF
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = (0x84 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        checksum = (0x84 + self._DeviceID) & 0xFF
        VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'Full': 0x01,
            'Natural': 0x00
        }

        checksum = (0x5C + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        VideoWallModeCmdString = pack('>BBBBBB', 0xAA, 0x5C, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        checksum = (0x5C + self._DeviceID) & 0xFF
        VideoWallModeCmdString = pack('>BBBBB', 0xAA, 0x5C, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Full',
            b'\x00': 'Natural'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVideoWallSize(self, value, qualifier):

        rowState = {
            '1': 0x10,
            '2': 0x20,
            '3': 0x30,
            '4': 0x40,
            '5': 0x50,
            '6': 0x60,
            '7': 0x70,
            '8': 0x80,
            '9': 0x90,
            '10': 0xA0,
            '11': 0xB0,
            '12': 0xC0,
            '13': 0xD0,
            '14': 0xE0,
            '15': 0xF0,
        }
        row = rowState[qualifier['Row']]
        column = int(qualifier['Column'])
        displayNum = int(value)

        if 0 < column <= 15 and 0 < displayNum <= 100:
            size = row + column
            if row <= 0x60 and column <= 15 and displayNum <= 90:
                Valid = True
            elif row <= 0x70 and column < 15 and displayNum <= 98:
                Valid = True
            elif row <= 0x80 and column < 13 and displayNum <= 96:
                Valid = True
            elif row <= 0x90 and column < 12 and displayNum <= 99:
                Valid = True
            elif row <= 0xA0 and column < 11:
                Valid = True
            elif row <= 0xB0 and column < 10 and displayNum <= 99:
                Valid = True
            elif row <= 0xC0 and column < 9 and displayNum <= 96:
                Valid = True
            elif row <= 0xD0 and column < 8 and displayNum <= 91:
                Valid = True
            elif row <= 0xE0 and column < 8 and displayNum <= 98:
                Valid = True
            elif row <= 0xF0 and column < 7 and displayNum <= 90:
                Valid = True
            else:
                Valid = False

            if Valid:
                checksum = (0x89 + self._DeviceID + 0x02 + size + displayNum) & 0xFF
                VideoWallSizeCmdString = pack('>BBBBBBB', 0xAA, 0x89, self._DeviceID, 0x02, size, displayNum, checksum)
                self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        checksum = (0x89 + self._DeviceID) & 0xFF
        VideoWallSizeCmdString = pack('>BBBBB', 0xAA, 0x89, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Volume', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        value = str(ord(match.group('value')))  # Display Num - Value
        value2 = ord(match.group('size'))
        if value2 < 0x20:  # row 1
            row = '1'
            value3 = value2 - 0x10
        elif value2 < 0x30:  # row 2
            row = '2'
            value3 = value2 - 0x20
        elif value2 < 0x40:  # row 3
            row = '3'
            value3 = value2 - 0x30
        elif value2 < 0x50:  # row 4
            row = '4'
            value3 = value2 - 0x40
        elif value2 < 0x60:  # row 5
            row = '5'
            value3 = value2 - 0x50
        elif value2 < 0x70:  # row 6
            row = '6'
            value3 = value2 - 0x60
        elif value2 < 0x80:  # row 7
            row = '7'
            value3 = value2 - 0x70
        elif value2 < 0x90:  # row 8
            row = '8'
            value3 = value2 - 0x80
        elif value2 < 0xA0:  # row 9
            row = '9'
            value3 = value2 - 0x90
        elif value2 < 0xB0:  # row 10
            row = '10'
            value3 = value2 - 0xA0
        elif value2 < 0xC0:  # row 11
            row = '11'
            value3 = value2 - 0xB0
        elif value2 < 0xD0:  # row 12
            row = '12'
            value3 = value2 - 0xC0
        elif value2 < 0xE0:  # row 13
            row = '13'
            value3 = value2 - 0xD0
        elif value2 < 0xF0:  # row 14
            row = '14'
            value3 = value2 - 0xE0
        elif value2 < 0xF7:  # row 15
            row = '15'
            value3 = value2 - 0xF0

        qualifier = {
            'Column': str(value3),
            'Row': row
        }

        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = (0x12 + self._DeviceID + 0x01 + value) & 0xFF
            VolumeCmdString = pack('>BBBBBB', 0xAA, 0x12, self._DeviceID, 0x01, value, checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = (0x12 + self._DeviceID) & 0xFF
        VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 254:
            self.Discard('Inappropriate Command ' + command)
        else:

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        Error = {
            b'\x11': 'Power',
            b'\x12': 'Volume',
            b'\x13': 'AudioMute',
            b'\x14': 'Input',
            b'\x18': 'AspectRatio',
            b'\x36': 'IRControl',
            b'\x3C': 'PIPMode',
            b'\x5C': 'VideoWallMode',
            b'\x5D': 'ExecutiveMode',
            b'\x84': 'VideoWall',
            b'\x89': 'VideoWallSize',
            b'\x3D': 'AutoImage',
            b'\xB0': 'MenuNavigation'
        }
        self.Error(['Device ID: {0}, Command: {1}, Error Code: {2}'.format(match.group(1)[0], Error[match.group(2)], match.group(3)[0])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_10_1761_0(self):

        self.ValueState = {
            'PC': 0x14,
            'DVI': 0x18,
            'MagicInfo': 0x20,
            'AV': 0x0C,
            'DTV': 0x40,
            'RF (TV)': 0x30,
            'HDMI': 0x21,
            'MagicInfo Lite': 0x60,
            'WiDi/Screen Mirroring': 0x61
        }

        self.ValueValues = {
            b'\x14': 'PC',
            b'\x18': 'DVI',
            b'\x20': 'MagicInfo',
            b'\x0C': 'AV',
            b'\x40': 'DTV',
            b'\x1F': 'DVI - VIDEO',
            b'\x22': 'HDMI 1 PC',
            b'\x21': 'HDMI',
            b'\x30': 'RF (TV)',
            b'\x60': 'MagicInfo Lite',
            b'\x61': 'WiDi/Screen Mirroring'
        }

    def smsg_10_1761_1(self):

        self.ValueState = {
            'PC': 0x14,
            'DVI': 0x18,
            'MagicInfo': 0x20,
            'AV': 0x0C,
            'DTV': 0x40,
            'DisplayPort': 0x25,
            'HDMI': 0x21,
            'RF (TV)': 0x30,
            'MagicInfo Lite': 0x60,
            'WiDi/Screen Mirroring': 0x61
        }

        self.ValueValues = {
            b'\x14': 'PC',
            b'\x18': 'DVI',
            b'\x20': 'MagicInfo',
            b'\x0C': 'AV',
            b'\x40': 'DTV',
            b'\x25': 'DisplayPort',
            b'\x1F': 'DVI - VIDEO',
            b'\x22': 'HDMI 1 PC',
            b'\x21': 'HDMI',
            b'\x30': 'RF (TV)',
            b'\x60': 'MagicInfo Lite',
            b'\x61': 'WiDi/Screen Mirroring'
        }

    def smsg_10_1761_2(self):

        self.ValueState = {
            'PC': 0x14,
            'DVI': 0x18,
            'MagicInfo': 0x20,
            'AV': 0x0C,
            'DTV': 0x40,
            'DisplayPort': 0x25,
            'HDMI 1': 0x21,
            'HDMI 2': 0x23,
            'RF (TV)': 0x30,
            'MagicInfo Lite': 0x60,
            'WiDi/Screen Mirroring': 0x61
        }

        self.ValueValues = {
            b'\x14': 'PC',
            b'\x18': 'DVI',
            b'\x20': 'MagicInfo',
            b'\x0C': 'AV',
            b'\x40': 'DTV',
            b'\x25': 'DisplayPort',
            b'\x1F': 'DVI - VIDEO',
            b'\x22': 'HDMI 1 PC',
            b'\x24': 'HDMI 2 PC',
            b'\x21': 'HDMI 1',
            b'\x23': 'HDMI 2',
            b'\x30': 'RF (TV)',
            b'\x60': 'MagicInfo Lite',
            b'\x61': 'WiDi/Screen Mirroring'
        }

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
                    except:
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
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands.get(command, None)
        if Command:
            Status = Command['Status']
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Status = Status[qualifier[Parameter]]
                    except KeyError:
                        return None
            try:
                return Status['Live']
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
