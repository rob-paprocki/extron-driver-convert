from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = b'\x01'

        self.Models = {
            'QM85D': self.smsg_10_863_QM,
            'LH55OMD': self.smsg_10_863_LH,
            'LH75OMD': self.smsg_10_863_LH,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3ScreenMode': {'Parameters': ['Mode', 'Sound', 'Size', 'Main Picture Size', 'Sub 1 Source', 'Sub 1 Picture Size', 'Sub 2 Source', 'Sub 2 Picture Size'], 'Status': {}},
            '4ScreenMode': {'Parameters': ['Mode', 'Sound', 'Size', 'Main Picture Size', 'Sub 1 Source', 'Sub 1 Picture Size', 'Sub 2 Source', 'Sub 2 Picture Size', 'Sub 3 Source', 'Sub 3 Picture Size'], 'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'Input': {'Status': {}},
            'KeysLock': {'Status': {}},
            'Mute': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'SafetyLock': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'VideoWallSize': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x18(\x01|\x04|\x31|\x0B)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5F(\x01|\x00)[\x00-\xFF]'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14(\x14|\x18|\x0C|\x08|\x20|\x21|\x23|\x1F|\x30|\x31|\x40|\x25)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x77(\x01|\x00)[\x00-\xFF]'), self.__MatchKeysLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13(\x01|\x00)[\x00-\xFF]'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x89([\x00-\xFF])([\x00-\x64])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\xFE'
        elif value == '0':
            self._DeviceID = b'\xFF'
        elif 0 < int(value) <= 99:
            self._DeviceID = pack('>B', int(value))
        else:
            self.Error(['DeviceID is set to an invalid value. It should be a number between 0 - 99 or Broadcast.'])

    def Set3ScreenMode(self, value, qualifier):

        ModeStates = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        mode = ModeStates[qualifier['Mode']]

        SoundStates = {
            'Main Screen': b'\x00',
            'Sub Screen 1': b'\x01',
            'Sub Screen 2': b'\x02',
            'Sub Screen 3': b'\x03'
        }

        sound = SoundStates[qualifier['Sound']]

        SizeStates = {
            'Mode 1': b'\x00',
            'Mode 2': b'\x01',
            'Mode 3': b'\x02',
            'Mode 4 (960:960)': b'\x03',
            'Mode 5 (1440:480)': b'\x04',
            'Mode 6 (1280:640)': b'\x05'
        }

        size = SizeStates[qualifier['Size']]

        MainPictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        mainsize = MainPictureSizeStates[qualifier['Main Picture Size']]

        SourceStates = {
            'TV (DTV)': b'\x40',
            'AV 1 (AV)': b'\x0C',
            'Component': b'\x08',
            'PC': b'\x14',
            'DVI': b'\x18',
            'DisplayPort': b'\x25',
            'DisplayPort 2': b'\x26',
            'DisplayPort 3': b'\x27',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'HDMI 3': b'\x31',
            'Plug In Module': b'\x50'
        }

        sub1source = SourceStates[qualifier['Sub 1 Source']]
        sub2source = SourceStates[qualifier['Sub 2 Source']]

        Sub1PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub1size = Sub1PictureSizeStates[qualifier['Sub 1 Picture Size']]

        Sub2PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub2size = Sub2PictureSizeStates[qualifier['Sub 2 Picture Size']]

        if self._DeviceID == b'\xFE':
            checksum = pack('>B', (0xB2 + self._DeviceID[0] + 0x08 + mode[0] + sound[0] + size[0] + mainsize[0] + sub1source[0] + sub1size[0] + sub2source[0] + sub2size[0]) & 0xFF)
            ScreenModeCmdString = b'\xAA\xB2' + self._DeviceID + b'\x08' + mode + sound + size + mainsize + sub1source + sub1size + sub2source + sub2size + checksum
            self.__SetHelper('3ScreenMode', ScreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set3ScreenMode')

    def Set4ScreenMode(self, value, qualifier):

        ModeStates = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        mode = ModeStates[qualifier['Mode']]

        SoundStates = {
            'Main Screen': b'\x00',
            'Sub Screen 1': b'\x01',
            'Sub Screen 2': b'\x02',
            'Sub Screen 3': b'\x03'
        }

        sound = SoundStates[qualifier['Sound']]

        SizeStates = {
            'Mode 1': b'\x00',
            'Mode 2': b'\x01',
            'Mode 3': b'\x02',
            'Mode 4 (960:960)': b'\x03',
            'Mode 5 (1440:480)': b'\x04',
            'Mode 6 (1280:640)': b'\x05'
        }

        size = SizeStates[qualifier['Size']]

        MainPictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        mainsize = MainPictureSizeStates[qualifier['Main Picture Size']]

        SourceStates = {
            'TV (DTV)': b'\x40',
            'AV 1 (AV)': b'\x0C',
            'Component': b'\x08',
            'PC': b'\x14',
            'DVI': b'\x18',
            'DisplayPort': b'\x25',
            'DisplayPort 2': b'\x26',
            'DisplayPort 3': b'\x27',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'HDMI 3': b'\x31',
            'Plug In Module': b'\x50'
        }

        sub1source = SourceStates[qualifier['Sub 1 Source']]
        sub2source = SourceStates[qualifier['Sub 2 Source']]
        sub3source = SourceStates[qualifier['Sub 3 Source']]

        Sub1PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub1size = Sub1PictureSizeStates[qualifier['Sub 1 Picture Size']]

        Sub2PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub2size = Sub2PictureSizeStates[qualifier['Sub 2 Picture Size']]

        Sub3PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub3size = Sub3PictureSizeStates[qualifier['Sub 3 Picture Size']]

        if self._DeviceID == b'\xFE':
            checksum = pack('>B', (0xB2 + self._DeviceID[0] + 0x0A + mode[0] + sound[0] + size[0] + mainsize[0] + sub1source[0] + sub1size[0] + sub2source[0] + sub2size[0] + sub3source[0] + sub3size[0]) & 0xFF)
            ScreenModeCmdString = b'\xAA\xB2' + self._DeviceID + b'\x0A' + mode + sound + size + mainsize + sub1source + sub1size + sub2source + sub2size + sub3source + sub3size + checksum
            self.__SetHelper('4ScreenMode', ScreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set4ScreenMode')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\x01',
            'Zoom': b'\x04',
            'Wide Zoom': b'\x31',
            '4:3': b'\x0B'
        }
        checksum = pack('>B', (0x18 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        AspectRatioCmdString = b'\xAA\x18' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        checksum = pack('>B', (0x18 + self._DeviceID[0]) & 0xFF)
        AspectRatioCmdString = b'\xAA\x18' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x31': 'Wide Zoom',
            '\x0B': '4:3'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        checksum = pack('>B', (0x3D + self._DeviceID[0] + 0x01) & 0xFF)
        AutoImageCmdString = b'\xAA\x3D' + self._DeviceID + b'\x01\x00' + checksum
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x5F + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        ButtonLockCmdString = b'\xAA\x5F' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        checksum = pack('>B', (0x5F + self._DeviceID[0]) & 0xFF)
        ButtonLockCmdString = b'\xAA\x5F' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ButtonLock', value, None)

    def SetInput(self, value, qualifier):

        checksum = pack('>B', (0x14 + self._DeviceID[0] + 0x01 + self.input_states[value][0]) & 0xFF)
        InputCmdString = b'\xAA\x14' + self._DeviceID + b'\x01' + self.input_states[value] + checksum
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        checksum = pack('>B', (0x14 + self._DeviceID[0]) & 0xFF)
        InputCmdString = b'\xAA\x14' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.input_query_states[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeysLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x77 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        KeysLockCmdString = b'\xAA\x77' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('KeysLock', KeysLockCmdString, value, qualifier)

    def UpdateKeysLock(self, value, qualifier):

        checksum = pack('>B', (0x77 + self._DeviceID[0]) & 0xFF)
        KeysLockCmdString = b'\xAA\x77' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('KeysLock', KeysLockCmdString, value, qualifier)

    def __MatchKeysLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('KeysLock', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x13 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        MuteCmdString = b'\xAA\x13' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        checksum = pack('>B', (0x13 + self._DeviceID[0]) & 0xFF)
        MuteCmdString = b'\xAA\x13' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        checksum = pack('>B', (0x3C + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        PIPModeCmdString = b'\xAA\x3C' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        checksum = pack('>B', (0x3C + self._DeviceID[0]) & 0xFF)
        PIPModeCmdString = b'\xAA\x3C' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        checksum = pack('>B', (0x11 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        PowerCmdString = b'\xAA\x11' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        checksum = pack('>B', (0x11 + self._DeviceID[0]) & 0xFF)
        PowerCmdString = b'\xAA\x11' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSafetyLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x5D + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        SafetyLockCmdString = b'\xAA\x5D' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def UpdateSafetyLock(self, value, qualifier):

        checksum = pack('>B', (0x5D + self._DeviceID[0]) & 0xFF)
        SafetyLockCmdString = b'\xAA\x5D' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def __MatchSafetyLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SafetyLock', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        checksum = pack('>B', (0x84 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        VideoWallCmdString = b'\xAA\x84' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        checksum = pack('>B', (0x84 + self._DeviceID[0]) & 0xFF)
        VideoWallCmdString = b'\xAA\x84' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x01',
            'Natural': b'\x00'
        }

        checksum = pack('>B', (0x5C + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        VideoWallModeCmdString = b'\xAA\x5C' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        checksum = pack('>B', (0x5C + self._DeviceID[0]) & 0xFF)
        VideoWallModeCmdString = b'\xAA\x5C' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'Full',
            '\x00': 'Natural'
        }

        value = ValueStateValues[match.group(1).decode()]
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
        rowValue = int(qualifier['Row'])
        column = int(qualifier['Column'])
        displayNum = int(value)

        if 0 < column <= 15 and 0 < rowValue <= 15:
            if 0 < displayNum <= 100:
                row = rowState[qualifier['Row']]
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
                    checksum = int(hex(0x89 + self._DeviceID[0] + 0x02 + size + displayNum)[-2:], 16)
                    VideoWallSizeCmdString = pack('>BBBBBBB', 0xAA, 0x89, self._DeviceID[0], 0x02, size, displayNum, checksum)
                    self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        checksum = int(hex(0x89 + self._DeviceID[0])[-2:], 16)
        VideoWallSizeCmdString = pack('>BBBBB', 0xAA, 0x89, self._DeviceID[0], 0x00, checksum)
        self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        value = str(ord(match.group(2).decode()))
        value2 = ord(match.group(1))
        if value2 < 0x20:
            row = '1'
            value3 = value2 - 0x10
        elif value2 < 0x30:
            row = '2'
            value3 = value2 - 0x20
        elif value2 < 0x40:
            row = '3'
            value3 = value2 - 0x30
        elif value2 < 0x50:
            row = '4'
            value3 = value2 - 0x40
        elif value2 < 0x60:
            row = '5'
            value3 = value2 - 0x50
        elif value2 < 0x70:
            row = '6'
            value3 = value2 - 0x60
        elif value2 < 0x80:
            row = '7'
            value3 = value2 - 0x70
        elif value2 < 0x90:
            row = '8'
            value3 = value2 - 0x80
        elif value2 < 0xA0:
            row = '9'
            value3 = value2 - 0x90
        elif value2 < 0xB0:
            row = '10'
            value3 = value2 - 0xA0
        elif value2 < 0xC0:
            row = '11'
            value3 = value2 - 0xB0
        elif value2 < 0xD0:
            row = '12'
            value3 = value2 - 0xC0
        elif value2 < 0xE0:
            row = '13'
            value3 = value2 - 0xD0
        elif value2 < 0xF0:
            row = '14'
            value3 = value2 - 0xE0
        elif value2 < 0xF7:
            row = '15'
            value3 = value2 - 0xF0
        qualifier = {'Column': str(value3), 'Row': row}

        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = pack('>B', (0x12 + self._DeviceID[0] + 0x01 + value) & 0xFF)
            VolumeCmdString = b'\xAA\x12' + self._DeviceID + b'\x01' + pack('>B', value) + checksum
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = pack('>B', (0x12 + self._DeviceID[0]) & 0xFF)
        VolumeCmdString = b'\xAA\x12' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1)[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\xFE':
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
        self.Error(['Device Id: {0}, Command: {1}, Error: {2}'.format(match.group(1), match.group(2), match.group(3))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_10_863_LH(self):

        self.input_states = {
            'PC': b'\x14',
            'DVI': b'\x18',
            'Input Source': b'\x0C',
            'Component': b'\x08',
            'MagicInfo': b'\x20',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'RF(TV)': b'\x30',
            'DTV': b'\x40',
            'DisplayPort': b'\x25'
        }

        self.input_query_states = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x0C': 'Input Source',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x21': 'HDMI 1',
            '\x23': 'HDMI 2',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x25': 'DisplayPort',
            '\x1F': 'DVI video'
        }

    def smsg_10_863_QM(self):

        self.input_states = {
            'PC': b'\x14',
            'DVI': b'\x18',
            'Input Source': b'\x0C',
            'Component': b'\x08',
            'MagicInfo': b'\x20',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'RF(TV)': b'\x30',
            'DTV': b'\x40',
            'DisplayPort': b'\x25',
            'HDMI 3': b'\x31'
        }

        self.input_query_states = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x0C': 'Input Source',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x21': 'HDMI 1',
            '\x23': 'HDMI 2',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x25': 'DisplayPort',
            '\x1F': 'DVI video',
            '\x31': 'HDMI 3'
        }

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
                    except:
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
        except:
            return None

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self.Models = {
            'LH55OMD': self.smsg_10_863_LH,
            'LH75OMD': self.smsg_10_863_LH,
            'QM85D': self.smsg_10_863_QM,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3ScreenMode': {'Parameters': ['Mode', 'Sound', 'Size', 'Main Picture Size', 'Sub 1 Source', 'Sub 1 Picture Size', 'Sub 2 Source', 'Sub 2 Picture Size'], 'Status': {}},
            '4ScreenMode': {'Parameters': ['Mode', 'Sound', 'Size', 'Main Picture Size', 'Sub 1 Source', 'Sub 1 Picture Size', 'Sub 2 Source', 'Sub 2 Picture Size', 'Sub 3 Source', 'Sub 3 Picture Size'], 'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'Input': {'Status': {}},
            'KeysLock': {'Status': {}},
            'Mute': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'SafetyLock': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'VideoWallSize': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\xFE'
        elif value == '0':
            self._DeviceID = b'\xFF'
        elif 0 < int(value) <= 99:
            self._DeviceID = pack('>B', int(value))
        else:
            self.Error(['DeviceID is set to an invalid value. It should be a number between 0 - 99 or Broadcast.'])

    def Set3ScreenMode(self, value, qualifier):

        ModeStates = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        mode = ModeStates[qualifier['Mode']]

        SoundStates = {
            'Main Screen': b'\x00',
            'Sub Screen 1': b'\x01',
            'Sub Screen 2': b'\x02',
            'Sub Screen 3': b'\x03'
        }

        sound = SoundStates[qualifier['Sound']]

        SizeStates = {
            'Mode 1': b'\x00',
            'Mode 2': b'\x01',
            'Mode 3': b'\x02',
            'Mode 4 (960:960)': b'\x03',
            'Mode 5 (1440:480)': b'\x04',
            'Mode 6 (1280:640)': b'\x05'
        }

        size = SizeStates[qualifier['Size']]

        MainPictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        mainsize = MainPictureSizeStates[qualifier['Main Picture Size']]

        SourceStates = {
            'TV (DTV)': b'\x40',
            'AV 1 (AV)': b'\x0C',
            'Component': b'\x08',
            'PC': b'\x14',
            'DVI': b'\x18',
            'DisplayPort': b'\x25',
            'DisplayPort 2': b'\x26',
            'DisplayPort 3': b'\x27',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'HDMI 3': b'\x31',
            'Plug In Module': b'\x50'
        }

        sub1source = SourceStates[qualifier['Sub 1 Source']]
        sub2source = SourceStates[qualifier['Sub 2 Source']]

        Sub1PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub1size = Sub1PictureSizeStates[qualifier['Sub 1 Picture Size']]

        Sub2PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub2size = Sub2PictureSizeStates[qualifier['Sub 2 Picture Size']]

        if self._DeviceID == b'\xFE':
            checksum = pack('>B', (0xB2 + self._DeviceID[0] + 0x08 + mode[0] + sound[0] + size[0] + mainsize[0] + sub1source[0] + sub1size[0] + sub2source[0] + sub2size[0]) & 0xFF)
            ScreenModeCmdString = b'\xAA\xB2' + self._DeviceID + b'\x08' + mode + sound + size + mainsize + sub1source + sub1size + sub2source + sub2size + checksum
            self.__SetHelper('3ScreenMode', ScreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set3ScreenMode')

    def Set4ScreenMode(self, value, qualifier):

        ModeStates = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        mode = ModeStates[qualifier['Mode']]

        SoundStates = {
            'Main Screen': b'\x00',
            'Sub Screen 1': b'\x01',
            'Sub Screen 2': b'\x02',
            'Sub Screen 3': b'\x03'
        }

        sound = SoundStates[qualifier['Sound']]

        SizeStates = {
            'Mode 1': b'\x00',
            'Mode 2': b'\x01',
            'Mode 3': b'\x02',
            'Mode 4 (960:960)': b'\x03',
            'Mode 5 (1440:480)': b'\x04',
            'Mode 6 (1280:640)': b'\x05'
        }

        size = SizeStates[qualifier['Size']]

        MainPictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        mainsize = MainPictureSizeStates[qualifier['Main Picture Size']]

        SourceStates = {
            'TV (DTV)': b'\x40',
            'AV 1 (AV)': b'\x0C',
            'Component': b'\x08',
            'PC': b'\x14',
            'DVI': b'\x18',
            'DisplayPort': b'\x25',
            'DisplayPort 2': b'\x26',
            'DisplayPort 3': b'\x27',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'HDMI 3': b'\x31',
            'Plug In Module': b'\x50'
        }

        sub1source = SourceStates[qualifier['Sub 1 Source']]
        sub2source = SourceStates[qualifier['Sub 2 Source']]
        sub3source = SourceStates[qualifier['Sub 3 Source']]

        Sub1PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub1size = Sub1PictureSizeStates[qualifier['Sub 1 Picture Size']]

        Sub2PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub2size = Sub2PictureSizeStates[qualifier['Sub 2 Picture Size']]

        Sub3PictureSizeStates = {
            'Full (Screen Fit)': b'\x09',
            'Original (Aspect Ratio)': b'\x20'
        }

        sub3size = Sub3PictureSizeStates[qualifier['Sub 3 Picture Size']]

        if self._DeviceID == b'\xFE':
            checksum = pack('>B', (0xB2 + self._DeviceID[0] + 0x0A + mode[0] + sound[0] + size[0] + mainsize[0] + sub1source[0] + sub1size[0] + sub2source[0] + sub2size[0] + sub3source[0] + sub3size[0]) & 0xFF)
            ScreenModeCmdString = b'\xAA\xB2' + self._DeviceID + b'\x0A' + mode + sound + size + mainsize + sub1source + sub1size + sub2source + sub2size + sub3source + sub3size + checksum
            self.__SetHelper('4ScreenMode', ScreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set4ScreenMode')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\x01',
            'Zoom': b'\x04',
            'Wide Zoom': b'\x31',
            '4:3': b'\x0B'
        }
        checksum = pack('>B', (0x18 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        AspectRatioCmdString = b'\xAA\x18' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        checksum = pack('>B', (0x3D + self._DeviceID[0] + 0x01) & 0xFF)
        AutoImageCmdString = b'\xAA\x3D' + self._DeviceID + b'\x01\x00' + checksum
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x5F + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        ButtonLockCmdString = b'\xAA\x5F' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        checksum = pack('>B', (0x14 + self._DeviceID[0] + 0x01 + self.input_states[value][0]) & 0xFF)
        InputCmdString = b'\xAA\x14' + self._DeviceID + b'\x01' + self.input_states[value] + checksum
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeysLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x77 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        KeysLockCmdString = b'\xAA\x77' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('KeysLock', KeysLockCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x13 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        MuteCmdString = b'\xAA\x13' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        checksum = pack('>B', (0x3C + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        PIPModeCmdString = b'\xAA\x3C' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        checksum = pack('>B', (0x11 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        PowerCmdString = b'\xAA\x11' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetSafetyLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x5D + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        SafetyLockCmdString = b'\xAA\x5D' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        checksum = pack('>B', (0x84 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        VideoWallCmdString = b'\xAA\x84' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x01',
            'Natural': b'\x00'
        }

        checksum = pack('>B', (0x5C + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        VideoWallModeCmdString = b'\xAA\x5C' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

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
        rowValue = int(qualifier['Row'])
        column = int(qualifier['Column'])
        displayNum = int(value)

        if 0 < column <= 15 and 0 < rowValue <= 15:
            if 0 < displayNum <= 100:
                row = rowState[qualifier['Row']]
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
                    checksum = int(hex(0x89 + self._DeviceID[0] + 0x02 + size + displayNum)[-2:], 16)
                    VideoWallSizeCmdString = pack('>BBBBBBB', 0xAA, 0x89, self._DeviceID[0], 0x02, size, displayNum, checksum)
                    self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetVideoWallSize')
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = pack('>B', (0x12 + self._DeviceID[0] + 0x01 + value) & 0xFF)
            VolumeCmdString = b'\xAA\x12' + self._DeviceID + b'\x01' + pack('>B', value) + checksum
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def smsg_10_863_LH(self):

        self.input_states = {
            'PC': b'\x14',
            'DVI': b'\x18',
            'Input Source': b'\x0C',
            'Component': b'\x08',
            'MagicInfo': b'\x20',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'RF(TV)': b'\x30',
            'DTV': b'\x40',
            'DisplayPort': b'\x25'
        }

    def smsg_10_863_QM(self):

        self.input_states = {
            'PC': b'\x14',
            'DVI': b'\x18',
            'Input Source': b'\x0C',
            'Component': b'\x08',
            'MagicInfo': b'\x20',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'RF(TV)': b'\x30',
            'DTV': b'\x40',
            'DisplayPort': b'\x25',
            'HDMI 3': b'\x31'
        }

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
