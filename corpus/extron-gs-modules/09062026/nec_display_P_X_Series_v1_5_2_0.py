from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack
from binascii import hexlify


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
        self.Models = {
            'P403': self.nec_10_185_A,
            'P463': self.nec_10_185_A,
            'P553': self.nec_10_185_A,
            'X554UN': self.nec_10_185_A,
            'X554UNS': self.nec_10_185_A,
            'X464UNV': self.nec_10_185_A,
            'X464UN': self.nec_10_185_A,
            'P703': self.nec_10_185_A,
            'P801': self.nec_10_185_A,
            'X464UN-TMX9P': self.nec_10_185_A,
            'X464UNS': self.nec_10_185_A,
            'UN551S': self.nec_10_185_B,
            'UN551VS': self.nec_10_185_B,
            'UN551S-TMX9P': self.nec_10_185_B,
            'X555UNS': self.nec_10_185_B,
            'X555UNV': self.nec_10_185_B,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioInput': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'Backlight': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'ChannelNumber': {'Parameters': ['Device ID'], 'Status': {}},
            'ClosedCaption': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Mute': {'Parameters': ['Device ID'], 'Status': {}},
            'Overscan': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'ScreenMute': {'Parameters': ['Device ID'], 'Status': {}},
            'SignalInformation': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixEnable': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixComp': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixPosition': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TVChannelStep': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020002700[01][0-9]{4}000([0-7])\x03'),
                                self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x0200022E00000B000([0-9A])\x03'),
                                self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020000100[01][0-9]{4}00([0-5][0-9A-F]|6[0-4])\x03'),
                                self.__MatchBacklight, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020000920[01][0-9]{4}00([0-5][0-9A-F]|6[0-4])\x03'),
                                self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020010840[01][0-9]{4}000([0-9])\x03'),
                                self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020000120[01][0-9]{4}00([0-5][0-9A-F]|6[0-4])\x03'),
                                self.__MatchContrast, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x0201'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020000600[01][0-9]{4}00([0-9A-F]{2})\x03'),
                                self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x0200008D000[0-9]{4}00([0-2])\x03'),
                                self.__MatchMute, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020002E30[01][0-9]{4}000([12])\x03'),
                                self.__MatchOverscan, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020002730[01][0-9]{4}00([0-9A-F]{2})\x03'),
                                self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020002720[01][0-9]{4}000([1-6])\x03'),
                                self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020010B90[01][0-9]{4}00([0-8][0-9])\x03'),
                                self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020200D6000004000([1-4])\x03'), self.__MatchPower,
                                None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020010B60[01][0-9]{4}000([12])\x03'),
                                self.__MatchScreenMute, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020002EA0[01][0-9]{4}000([0-2])\x03'),
                                self.__MatchSignalInformation, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020002D30[01][0-9]{4}000([12])\x03'),
                                self.__MatchTileMatrixEnable, None)
            self.AddMatchString(re.compile(b'\x0100([\x41-\xA4]).*\x020000620[01][0-9]{4}00([0-5][0-9A-F]|6[0-4])\x03'),
                                self.__MatchVolume, None)

    def SetQualifierDeviceID(self, value):
        if value.isdigit():
            if 1 <= int(value) <= 100:
                return 0x40 + int(value)
            else:
                return 0
        elif value == 'Broadcast':
            return 0x2A
        elif 'A' <= value <= 'J':
            return value.encode()[0] - 0x10
        return 0

    def MatchIDConversion(self, value):
        if 0x41 <= ord(value) <= 0xA4:
            response = ord(value) - 64
            return str(response)
        return 0

    def SetAspectRatio(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'Normal': b'0E0A\x0202700001\x03',
                'Full': b'0E0A\x0202700002\x03',
                'Wide': b'0E0A\x0202700003\x03',
                'Zoom': b'0E0A\x0202700004\x03',
                'Dynamic': b'0E0A\x0202700006\x03',
                '1:1': b'0E0A\x0202700007\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('AspectRatio', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020270\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        StateNames = {
            '1': 'Normal',
            '2': 'Full',
            '3': 'Wide',
            '4': 'Zoom',
            '6': 'Dynamic',
            '7': '1:1'
        }
        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioInput(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, self.SetAudioInputState[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('AudioInput', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x02022E\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('AudioInput', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioInput')

    def __MatchAudioInput(self, match, tag):

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = self.GetAudioInputState[match.group(2).decode()]
        self.WriteStatus('AudioInput', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, b'0E0A\x02001E0001\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('AutoImage', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetBacklight(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            if 0 <= value <= 100:  # check is used for protection purposes only
                result = hexlify(value.to_bytes(1, 'big')).upper()

                buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02001000', result, b'\x03')
                checksum = 0
                for i in buffer:
                    checksum ^= i

                CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
                self.__SetHelper('Backlight', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetBacklight')
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020010\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Backlight', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBacklight')

    def __MatchBacklight(self, match, tag):

        value = match.group(2).decode()
        value = int(value, 16)

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        self.WriteStatus('Backlight', value, qualifier)

    def SetBrightness(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            if 0 <= value <= 100:  # check is used for protection purposes only
                result = hexlify(value.to_bytes(1, 'big')).upper()

                buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02009200', result, b'\x03')
                checksum = 0
                for i in buffer:
                    checksum ^= i

                CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
                self.__SetHelper('Brightness', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetBrightness')
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020092\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def __MatchBrightness(self, match, tag):

        value = match.group(2).decode()
        value = int(value, 16)

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        self.WriteStatus('Brightness', value, qualifier)

    def SetChannelNumber(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                '1': b'0A0C\x02C210000801\x03',
                '2': b'0A0C\x02C210000901\x03',
                '3': b'0A0C\x02C210000A01\x03',
                '4': b'0A0C\x02C210000B01\x03',
                '5': b'0A0C\x02C210000C01\x03',
                '6': b'0A0C\x02C210000D01\x03',
                '7': b'0A0C\x02C210000E01\x03',
                '8': b'0A0C\x02C210000F01\x03',
                '9': b'0A0C\x02C210001001\x03',
                '0': b'0A0C\x02C210001201\x03',
                '-': b'0A0C\x02C210004401\x03',
                'Enter': b'0A0C\x02C210004501\x03',
                'Exit': b'0A0C\x02C210001F01\x03',
                'Return': b'0A0C\x02C210002A01\x03'
            }

            buffer = pack('>BB16s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('ChannelNumber', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelNumber')

    def SetClosedCaption(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            StateValues = {
                'CC1': b'0E0A\x0210840002\x03',
                'CC2': b'0E0A\x0210840003\x03',
                'CC3': b'0E0A\x0210840004\x03',
                'CC4': b'0E0A\x0210840005\x03',
                'Text 1': b'0E0A\x0210840006\x03',
                'Text 2': b'0E0A\x0210840007\x03',
                'Text 3': b'0E0A\x0210840008\x03',
                'Text 4': b'0E0A\x0210840009\x03',
                'Off': b'0E0A\x0210840001\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('ClosedCaption', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def UpdateClosedCaption(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x021084\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('ClosedCaption', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateClosedCaption')

    def __MatchClosedCaption(self, match, tag):

        StateNames = {
            '1': 'Off',
            '2': 'CC1',
            '3': 'CC2',
            '4': 'CC3',
            '5': 'CC4',
            '6': 'Text 1',
            '7': 'Text 2',
            '8': 'Text 3',
            '9': 'Text 4'
        }

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('ClosedCaption', value, qualifier)

    def SetContrast(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            if 0 <= value <= 100:  # check is used for protection purposes only
                result = hexlify(value.to_bytes(1, 'big')).upper()

                buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02001200', result, b'\x03')
                checksum = 0
                for i in buffer:
                    checksum ^= i

                CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
                self.__SetHelper('Contrast', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetContrast')
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020012\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Contrast', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateContrast')

    def __MatchContrast(self, match, tag):

        value = match.group(2).decode()
        value = int(value, 16)

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        self.WriteStatus('Contrast', value, qualifier)

    def SetInput(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:

            buffer = pack('>BB14s', 0x30, DeviceID, self.SetInputState[value])
            checksum = 0
            for i in buffer:
                checksum ^= i
            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('Input', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020060\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Input', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = self.GetInputState[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetMute(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            StateValues = {
                'On': b'0E0A\x02008D0001\x03',
                'Off': b'0E0A\x02008D0000\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('Mute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x02008D\x03')
        if DeviceID != 0:
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Mute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        StateNames = {
            '1': 'On',
            '2': 'Off',
            '0': 'Off'
        }
        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('Mute', value, qualifier)

    def SetOverscan(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'On': b'0E0A\x0202E30002\x03',
                'Off': b'0E0A\x0202E30001\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('Overscan', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOverscan')

    def UpdateOverscan(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202E3\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Overscan', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOverscan')

    def __MatchOverscan(self, match, tag):

        StateNames = {
            '2': 'On',
            '1': 'Off'
        }
        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('Overscan', value, qualifier)

    def SetPIPInput(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:

            buffer = pack('>BB14s', 0x30, DeviceID, self.SetPIPInputState[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('PIPInput', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020273\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('PIPInput', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPInput')

    def __MatchPIPInput(self, match, tag):

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = self.GetPIPInputState[match.group(2).decode()]
        self.WriteStatus('PIPInput', value, qualifier)

    def SetPIPMode(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'PIP': b'0E0A\x0202720002\x03',
                'POP': b'0E0A\x0202720003\x03',
                'Still': b'0E0A\x0202720004\x03',
                'Picture By Picture (Aspect)': b'0E0A\x0202720005\x03',
                'Picture By Picture (Full)': b'0E0A\x0202720006\x03',
                'Off': b'0E0A\x0202720001\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('PIPMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020272\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('PIPMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPMode')

    def __MatchPIPMode(self, match, tag):

        StateNames = {
            '2': 'PIP',
            '3': 'POP',
            '4': 'Still',
            '5': 'Picture By Picture (Aspect)',
            '6': 'Picture By Picture (Full)',
            '1': 'Off'
        }
        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('PIPMode', value, qualifier)

    def SetPIPSize(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB11s2sB', 0x30, DeviceID, b'0E0A\x0210B900', value.zfill(2).encode(), 0x03)
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('PIPSize', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0210B9\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('PIPSize', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPSize')

    def __MatchPIPSize(self, match, tag):

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}

        if match.group(2).decode() == '00':
            value = match.group(2).decode()[1]
        else:
            value = match.group(2).decode().lstrip('0')

        self.WriteStatus('PIPSize', value, qualifier)

    def SetPower(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'On': b'0A0C\x02C203D60001\x03',
                'Off': b'0A0C\x02C203D60004\x03'
            }

            buffer = pack('>BB16s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('Power', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0A06\x0201D6\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Power', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        StateNames = {
            '1': 'On',
            '2': 'Stand-by',
            '3': 'Suspend',
            '4': 'Off'
        }
        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}        
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('Power', value, qualifier)

    def SetScreenMute(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            StateValues = {
                'On': b'0E0A\x0210B60001\x03',
                'Off': b'0E0A\x0210B60002\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('ScreenMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenMute')

    def UpdateScreenMute(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0210B6\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('ScreenMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateScreenMute')

    def __MatchScreenMute(self, match, tag):

        StateNames = {
            '1': 'On',
            '2': 'Off'
        }
        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('ScreenMute', value, qualifier)

    def SetSignalInformation(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'On': b'0E0A\x0202EA0002\x03',
                'Off': b'0E0A\x0202EA0001\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('SignalInformation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalInformation')

    def UpdateSignalInformation(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202EA\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('SignalInformation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSignalInformation')

    def __MatchSignalInformation(self, match, tag):

        StateNames = {
            '2': 'On',
            '1': 'Off'
        }

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('SignalInformation', value, qualifier)

    def SetTileHMonitor(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            value = int(value)
            if 1 <= value <= 10:  # check is used for protection purposes only
                result = hexlify(value.to_bytes(1, 'big')).upper()

                buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D000', result, b'\x03')
                checksum = 0
                for i in buffer:
                    checksum ^= i

                CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
                self.__SetHelper('TileHMonitor', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetTileHMonitor')
        else:
            self.Discard('Invalid Command for SetTileHMonitor')

    def SetTileMatrixComp(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'On': b'0E0A\x0202D50002\x03',
                'Off': b'0E0A\x0202D50001\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('TileMatrixComp', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixComp')

    def SetTileMatrixEnable(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'On': b'0E0A\x0202D30002\x03',
                'Off': b'0E0A\x0202D30001\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('TileMatrixEnable', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixEnable')

    def UpdateTileMatrixEnable(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202D3\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('TileMatrixEnable', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTileMatrixEnable')

    def __MatchTileMatrixEnable(self, match, tag):

        StateNames = {
            '2': 'On',
            '1': 'Off'
        }
        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        value = StateNames[match.group(2).decode()]
        self.WriteStatus('TileMatrixEnable', value, qualifier)

    def SetTileMatrixPosition(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            value = int(value)
            if 1 <= value <= 100:  # check is used for protection purposes only
                result = hexlify(value.to_bytes(1, 'big')).upper()

                buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D200', result, b'\x03')
                checksum = 0
                for i in buffer:
                    checksum ^= i

                CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
                self.__SetHelper('TileMatrixPosition', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetTileMatrixPosition')
        else:
            self.Discard('Invalid Command for SetTileMatrixPosition')

    def SetTileVMonitor(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            value = int(value)
            if 1 <= value <= 10:  # check is used for protection purposes only
                result = hexlify(value.to_bytes(1, 'big')).upper()

                buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D100', result, b'\x03')
                checksum = 0
                for i in buffer:
                    checksum ^= i

                CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
                self.__SetHelper('TileVMonitor', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetTileVMonitor')
        else:
            self.Discard('Invalid Command for SetTileVMonitor')

    def SetTVChannelStep(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            StateValues = {
                'Up': b'0E0A\x02008B0001\x03',
                'Down': b'0E0A\x02008B0002\x03'
            }

            buffer = pack('>BB14s', 0x30, DeviceID, StateValues[value])
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
            self.__SetHelper('TVChannelStep', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTVChannelStep')

    def SetVolume(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            if 0 <= value <= 100:  # check is used for protection purposes only
                result = hexlify(value.to_bytes(1, 'big')).upper()

                buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02006200', result, b'\x03')
                checksum = 0
                for i in buffer:
                    checksum ^= i

                CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])
                self.__SetHelper('Volume', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVolume')
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020062\x03')
            checksum = 0
            for i in buffer:
                checksum ^= i

            CmdString = b''.join([b'\x01', buffer, pack('>B', checksum), b'\r'])

            self.__UpdateHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        value = match.group(2).decode()
        value = int(value, 16)

        qualifier = {'Device ID': self.MatchIDConversion(match.group(1))}
        self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast' or 'A' <= qualifier[
            'Device ID'] <= 'J':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        self.Error(['An error occurred'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def nec_10_185_A(self):

        self.SetAudioInputState = {
            'IN1': b'0E0A\x02022E0001\x03',
            'IN2': b'0E0A\x02022E0002\x03',
            'IN3': b'0E0A\x02022E0003\x03',
            'HDMI': b'0E0A\x02022E0004\x03',
            'Option': b'0E0A\x02022E0006\x03',
            'DisplayPort': b'0E0A\x02022E0007\x03',
            'DisplayPort2': b'0E0A\x02022E0008\x03',
            'DisplayPort3': b'0E0A\x02022E0009\x03',
            'HDMI2': b'0E0A\x02022E000A\x03'
        }

        self.GetAudioInputState = {
            '1': 'IN1',
            '2': 'IN2',
            '3': 'IN3',
            '4': 'HDMI',
            '6': 'Option',
            '7': 'DisplayPort',
            '8': 'DisplayPort2',
            '9': 'DisplayPort3',
            'A': 'HDMI2'
        }

        self.SetInputState = {
            'VGA': b'0E0A\x0200600001\x03',
            'RGB/HV': b'0E0A\x0200600002\x03',
            'DVI': b'0E0A\x0200600003\x03',
            'Option': b'0E0A\x020060000D\x03',
            'Video': b'0E0A\x0200600005\x03',
            'S-Video': b'0E0A\x0200600007\x03',
            'Y/Pb/Pr': b'0E0A\x020060000C\x03',
            'Y/Pb/Pr2': b'0E0A\x020060000E\x03',
            'DisplayPort': b'0E0A\x020060000F\x03',
            'DisplayPort2': b'0E0A\x0200600010\x03',
            'DisplayPort3': b'0E0A\x0200600080\x03',
            'HDMI': b'0E0A\x0200600011\x03',
            'HDMI2': b'0E0A\x0200600012\x03'
        }

        self.GetInputState = {
            '01': 'VGA',
            '02': 'RGB/HV',
            '03': 'DVI',
            '0D': 'Option',
            '05': 'Video',
            '07': 'S-Video',
            '0C': 'Y/Pb/Pr',
            '0E': 'Y/Pb/Pr2',
            '0F': 'DisplayPort',
            '10': 'DisplayPort2',
            '80': 'DisplayPort3',
            '11': 'HDMI',
            '12': 'HDMI2'
        }

        self.SetPIPInputState = {
            'VGA': b'0E0A\x0202730001\x03',
            'RGB/HV': b'0E0A\x0202730002\x03',
            'DVI': b'0E0A\x0202730003\x03',
            'Option': b'0E0A\x020273000D\x03',
            'Video': b'0E0A\x0202730005\x03',
            'S-Video': b'0E0A\x0202730007\x03',
            'Y/Pb/Pr': b'0E0A\x020273000C\x03',
            'Y/Pb/Pr2': b'0E0A\x020273000E\x03',
            'DisplayPort': b'0E0A\x020273000F\x03',
            'DisplayPort2': b'0E0A\x0202730010\x03',
            'DisplayPort3': b'0E0A\x0202730080\x03',
            'HDMI': b'0E0A\x0202730011\x03',
            'HDMI2': b'0E0A\x0202730012\x03'
        }

        self.GetPIPInputState = {
            '01': 'VGA',
            '02': 'RGB/HV',
            '03': 'DVI',
            '0D': 'Option',
            '05': 'Video',
            '07': 'S-Video',
            '0C': 'Y/Pb/Pr',
            '0E': 'Y/Pb/Pr2',
            '0F': 'DisplayPort',
            '10': 'DisplayPort2',
            '80': 'DisplayPort3',
            '11': 'HDMI',
            '12': 'HDMI2'
        }

    def nec_10_185_B(self):

        self.SetAudioInputState = {
            'IN1': b'0E0A\x02022E0001\x03',
            'IN2': b'0E0A\x02022E0002\x03',
            'HDMI': b'0E0A\x02022E0004\x03',
            'DisplayPort': b'0E0A\x02022E0007\x03'
        }

        self.GetAudioInputState = {
            '1': 'IN1',
            '2': 'IN2',
            '4': 'HDMI',
            '7': 'DisplayPort'
        }

        self.SetInputState = {
            'VGA': b'0E0A\x0200600001\x03',
            'DVI': b'0E0A\x0200600003\x03',
            'Y/Pb/Pr': b'0E0A\x020060000C\x03',
            'DisplayPort': b'0E0A\x020060000F\x03',
            'HDMI': b'0E0A\x0200600011\x03'
        }

        self.GetInputState = {
            '01': 'VGA',
            '03': 'DVI',
            '0C': 'Y/Pb/Pr',
            '0F': 'DisplayPort',
            '11': 'HDMI'
        }

        self.SetPIPInputState = {
            'VGA': b'0E0A\x0202730001\x03',
            'DVI': b'0E0A\x0202730003\x03',
            'Y/Pb/Pr': b'0E0A\x020273000C\x03',
            'DisplayPort': b'0E0A\x020273000F\x03',
            'HDMI': b'0E0A\x0202730011\x03'
        }

        self.GetPIPInputState = {
            '01': 'VGA',
            '03': 'DVI',
            '0C': 'Y/Pb/Pr',
            '0F': 'DisplayPort',
            '11': 'HDMI'
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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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

