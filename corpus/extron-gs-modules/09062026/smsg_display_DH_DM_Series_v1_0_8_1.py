from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceClass:
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
            'DH40D': self.smsg_10_557_1,
            'DH48D': self.smsg_10_557_1,
            'DH55D': self.smsg_10_557_1,
            'DM32D': self.smsg_10_557_3,
            'DM40D': self.smsg_10_557_1,
            'DM48D': self.smsg_10_557_1,
            'DM55D': self.smsg_10_557_1,
            'DM65D': self.smsg_10_557_1,
            'DM75D': self.smsg_10_557_1,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ChannelDiscreteCommand': {'Parameters': ['Tuner Mode', 'Signal Type'], 'Status': {}},
            'ChannelUpDown': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'InputSignalDetect': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'VideoWallSize': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x15(\x01|\x0B|\x10|\x18|\x05|\x06|\x0E|\x0F|\x0C|\x0D|\x09)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13(\x01|\x00)[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14(\x14|\x18|\x0C|\x50|\x08|\x20|\x1F|\x30|\x40|\x21|\x22|\x25)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x08\x41\x0D.{3}(\x01|\x00).{2}[\x00-\xFF]'), self.__MatchInputSignalDetect, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x04][\x41][\x89](?P<size>[\x00-\xFF])(?P<value>[\x00-\x64])(?P<checksum>[\x00-\xFF])'), self.__MatchVideoWallSize, None)
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
        elif 1 <= int(value) <= 224:
            self._DeviceID = pack('>B', int(value))
        else:
            self.Error(['DeviceID should be a value between 0 to 224 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        input = qualifier['Input']

        if (input == 'PC' or input == 'DVI' or input == 'HDMI1 PC') and (value == '4:3' or value == '16:9'):
            ValueStateValues = {
                '16:9': b'\x10',
                '4:3': b'\x18',
                'Zoom 1': b'\x05',
                'Zoom 2': b'\x06',
                'Smart View 1': b'\x0E',
                'Smart View 2': b'\x0F',
                'Wide Fit': b'\x0C',
                'Custom': b'\x0D',
                'Screen Fit': b'\x09'
            }
        else:
            ValueStateValues = {
                '16:9': b'\x01',
                '4:3': b'\x0B',
                'Zoom 1': b'\x05',
                'Zoom 2': b'\x06',
                'Smart View 1': b'\x0E',
                'Smart View 2': b'\x0F',
                'Wide Fit': b'\x0C',
                'Custom': b'\x0D',
                'Screen Fit': b'\x09'
            }

        checksum = pack('>B', (0x15 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        AspectRatioCmdString = b'\xAA\x15' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        checksum = pack('>B', (0x15 + self._DeviceID[0]) & 0xFF)
        AspectRatioCmdString = b'\xAA\x15' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01': '16:9',
            '\x0B': '4:3',
            '\x10': '16:9',
            '\x18': '4:3',
            '\x05': 'Zoom 1',
            '\x06': 'Zoom 2',
            '\x0E': 'Smart View 1',
            '\x0F': 'Smart View 2',
            '\x0C': 'Wide Fit',
            '\x0D': 'Custom',
            '\x09': 'Screen Fit',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00',
            'On': b'\x01'
        }
        checksum = pack('>B', (0x13 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        AudioMuteCmdString = b'\xAA\x13' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        checksum = pack('>B', (0x13 + self._DeviceID[0]) & 0xFF)
        AudioMuteCmdString = b'\xAA\x13' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        checksum = pack('>B', (0x3D + self._DeviceID[0] + 0x01) & 0xFF)
        AutoImageCmdString = b'\xAA\x3D' + self._DeviceID + b'\x01\x00' + checksum
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannelDiscreteCommand(self, value, qualifier):

        SignalTypeValues = {
            'Analog': 0x00,
            'Digital': 0x01
        }
        TunerModeValues = {
            'Air': 0x00,
            'Cable': 0x01
        }

        if value:
            signaltype = SignalTypeValues[qualifier['Signal Type']]
            tunermode = TunerModeValues[qualifier['Tuner Mode']]
            country = 0x01  # USA
            if '-' in value:  # Check if minor channel
                selminor = 0x01
            else:
                selminor = 0x00

            if selminor:  # If there is a minor channel
                index = 0
                for i in value:  # Parse out major and minor channel
                    if i != '-':
                        index += 1
                    else:
                        break
                majorChannel = int(value[:index])
                minorChannel = int(value[index + 1:])
            else:  # Otherwise minor channel is zero
                majorChannel = int(value)
                minorChannel = 0

            chhigh = majorChannel >> 8
            chlow = majorChannel % 256
            minorchhigh = minorChannel >> 8
            minorchlow = minorChannel % 256

            CKS = int(hex(0x1F + self._DeviceID[0] + country + signaltype + tunermode + chhigh + chlow + selminor + minorchhigh + minorchlow)[-2:], 16)
            ChannelCmdString = pack('>BBBBBBBBBBBBB', 0xAA, 0x17, self._DeviceID[0], 0x08, country, signaltype, tunermode, chhigh, chlow, selminor, minorchhigh,
                                    minorchlow, CKS)
            self.__SetHelper('ChannelDiscreteCommand', ChannelCmdString, value, qualifier)

    def SetChannelUpDown(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x00',
            'Down': b'\x01'
        }

        checksum = pack('>B', (0x61 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        ChannelUpDownCmdString = b'\xAA\x61' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('ChannelUpDown', ChannelUpDownCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x5D + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        ExecutiveModeCmdString = b'\xAA\x5D' + self._DeviceID + b'\x01' + ValueStateValues[value] + checksum
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        checksum = pack('>B', (0x5D + self._DeviceID[0]) & 0xFF)
        ExecutiveModeCmdString = b'\xAA\x5D' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        checksum = pack('>B', (0x14 + self._DeviceID[0] + 0x01 + self.ValueState[value][0]) & 0xFF)
        InputCmdString = b'\xAA\x14' + self._DeviceID + b'\x01' + self.ValueState[value] + checksum
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        checksum = pack('>B', (0x14 + self._DeviceID[0]) & 0xFF)
        InputCmdString = b'\xAA\x14' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.ValueValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalDetect(self, value, qualifier):

        checksum = pack('>B', (0x0D + self._DeviceID[0]) & 0xFF)
        InputSignalDetectCmdString = b'\xAA\x0D' + self._DeviceID + b'\x00' + checksum
        self.__UpdateHelper('InputSignalDetect', InputSignalDetectCmdString, value, qualifier)

    def __MatchInputSignalDetect(self, match, tag):

        ValueStateValues = {
            '\x00': 'Present',
            '\x01': 'Not Present'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputSignalDetect', value, None)

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
                CKS = pack('>B', (0x89 + self._DeviceID[0] + 0x02 + size + displayNum) & 0xFF)
                CmdString = pack('>BBBBBBB', 0xAA, 0x89, ord(self._DeviceID), 0x02, size, displayNum, ord(CKS))
                self.__SetHelper('VideoWallSize', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        CKS = pack('>B', (0x89 + self._DeviceID[0]) & 0xFF)
        VideoWallSizeCmdString = b'\xAA\x89' + self._DeviceID + b'\x00' + CKS
        self.__UpdateHelper('Volume', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        value = str(ord(match.group('value')))
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
        self.counter = 0
        self.Error(['Device Id: {0}, Command: {1}, Error: {2}'.format(match.group(1), match.group(2), match.group(3))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_10_557_1(self):
        self.ValueState = {
            'PC': b'\x14',
            'DVI': b'\x18',
            'Input Source': b'\x0C',
            'Component': b'\x08',
            'MagicInfo': b'\x20',
            'RF(TV)': b'\x30',
            'DTV': b'\x40',
            'HDMI1': b'\x21',
            'DisplayPort': b'\x25',
            'Plug In Module': b'\x50'
        }

        self.ValueValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x0C': 'Input Source',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x21': 'HDMI1',
            '\x22': 'HDMI1 PC',
            '\x25': 'DisplayPort',
            '\x1F': 'DVI video',
            '\x50': 'Plug In Module'
        }

    def smsg_10_557_3(self):

        self.ValueState = {
            'PC': b'\x14',
            'DVI': b'\x18',
            'Input Source': b'\x0C',
            'Component': b'\x08',
            'MagicInfo': b'\x20',
            'RF(TV)': b'\x30',
            'DTV': b'\x40',
            'HDMI1': b'\x21',
        }

        self.ValueValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x0C': 'Input Source',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x21': 'HDMI1',
            '\x22': 'HDMI1 PC',
            '\x1F': 'DVI video',
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
