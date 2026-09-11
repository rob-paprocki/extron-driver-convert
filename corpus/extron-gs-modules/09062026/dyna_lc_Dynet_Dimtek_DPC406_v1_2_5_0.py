from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import re


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AreaOff': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'ChannelLevelStatus': {'Parameters': ['Area', 'Channel'], 'Status': {}},
            'ClassicPreset': {'Parameters': ['Area', 'Fade Time', 'Preset'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Area'], 'Status': {}},
            'FadeArea': {'Parameters': ['Area', 'Level', 'Fade Time'], 'Status': {}},
            'FadeChannel': {'Parameters': ['Area', 'Level', 'Channel Offset', 'Fade Time'], 'Status': {}},
            'LinearChannel': {'Parameters': ['Area', 'Channel', 'Channel Level', 'Fade Time'], 'Status': {}},
            'LinearPreset': {'Parameters': ['Area', 'Preset', 'Fade Time'], 'Status': {}},
            'Panic': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'PresetStatus': {'Parameters': ['Area'], 'Status': {}},
            'ProgramtoCurrentPreset': {'Parameters': ['Area'], 'Status': {}},
            'RecallSavedPreset': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'ResetPreset': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'SaveCurrentPreset': {'Parameters': ['Area'], 'Status': {}},
            'StopFade': {'Parameters': ['Area', 'Channel'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x1c([\x00-\xFF])([\x00-\xFF])\x60[\x00-\xFF]([\x00-\xFF])\xFF[\x00-\xFF]'), self.__MatchChannelLevelStatus, None)
            self.AddMatchString(re.compile(b'\x1c([\x00-\xFF])([\x00-\x20])\x62\x00\x00\xFF[\x00-\xFF]'), self.__MatchPresetStatus, None)

    def SetAreaOff(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }

        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds', '13 seconds',
                          '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds', '19 seconds',
                          '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds', '25 seconds',
                          '26 seconds', '27 seconds', '28 seconds', '29 seconds', '30 seconds', '31 seconds',
                          '32 seconds', '33 seconds', '34 seconds', '35 seconds', '36 seconds', '37 seconds',
                          '38 seconds', '39 seconds', '40 seconds', '41 seconds', '42 seconds', '43 seconds',
                          '44 seconds', '45 seconds', '46 seconds', '47 seconds', '48 seconds', '49 seconds',
                          '50 seconds', '51 seconds', '52 seconds', '53 seconds', '54 seconds', '55 seconds',
                          '56 seconds', '57 seconds', '58 seconds', '59 seconds',
                          '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '6 minutes', '7 minutes',
                          '8 minutes', '9 minutes', '10 minutes', '11 minutes', '12 minutes', '13 minutes',
                          '14 minutes', '15 minutes', '16 minutes', '17 minutes', '18 minutes', '19 minutes',
                          '20 minutes')

        area = qualifier['Area']
        if area == 'All':
            area = 0
        fadetime = qualifier['Fade Time']

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and fadetime in FadeTimeStates:
                # Compute for Fade Time
                fade = int(fadetime.split()[0])
                if 'second' in fadetime:
                    fade *= 50  # 50 == 1 second
                else:
                    fade *= 3000  # 3000 == 1 minute

                fade_low = fade & 0xFF
                fade_high = fade >> 8

                # Compute for Checksum
                chksum = 0x1c + area + fade_low + 0x04 + fade_high + 0x00 + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                AreaOffCmdString = pack('>8B', 0x1c, area, fade_low, 0x04, fade_high, 0x00, 0xFF, chksum)
                self.__SetHelper('AreaOff', AreaOffCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetAreaOff')

    def UpdateChannelLevelStatus(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        ChannelConstraints = {
            'Min': 0,
            'Max': 255
        }
        area = qualifier['Area']
        if area == 'All':
            area = 0

        try:
            channel = int(qualifier['Channel'])
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            channel -= 1  # channel origin is 0
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and ChannelConstraints['Min'] <= channel <= ChannelConstraints['Max']:
                chksum = 0x1c + area + channel + 0x61 + 0x00 + 0x00 + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                ChannelLevelStatusCmdString = pack('>8B', 0x1c, area, channel, 0x61, 0x00, 0x00, 0xFF, chksum)
                self.__UpdateHelper('ChannelLevelStatus', ChannelLevelStatusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateChannelLevelStatus')

    def __MatchChannelLevelStatus(self, match, tag):

        qualifier = {}
        area = unpack('B', match.group(1))[0]
        if area == 0:
            qualifier['Area'] = 'All'
        else:
            qualifier['Area'] = str(area)
        channel = unpack('B', match.group(2))[0]
        qualifier['Channel'] = str(channel + 1)  # channel origin is 0
        current_level = unpack('B', match.group(3))[0]
        if current_level == 255:
            current_level = 0
        elif current_level == 128:
            current_level = 50
        elif current_level == 1:
            current_level = 100
        else:
            current_level = 255 - current_level
            current_level *= 101
            current_level /= 255

        value = round(current_level)
        self.WriteStatus('ChannelLevelStatus', value, qualifier)

    def SetClassicPreset(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        # (OpCode, Bank)
        ValueStateValues = {
            'Preset 1'  : (0x00, 0x00),   
            'Preset 2'  : (0x01, 0x00), 
            'Preset 3'  : (0x02, 0x00), 
            'Preset 4'  : (0x03, 0x00), 
            'Preset 5'  : (0x0a, 0x00), 
            'Preset 6'  : (0x0b, 0x00), 
            'Preset 7'  : (0x0c, 0x00), 
            'Preset 8'  : (0x0d, 0x00), 
            'Preset 9'  : (0x00, 0x01), 
            'Preset 10' : (0x01, 0x01), 
            'Preset 11' : (0x02, 0x01), 
            'Preset 12' : (0x03, 0x01), 
            'Preset 13' : (0x0a, 0x01), 
            'Preset 14' : (0x0b, 0x01), 
            'Preset 15' : (0x0c, 0x01), 
            'Preset 16' : (0x0d, 0x01), 
            'Preset 17' : (0x00, 0x02), 
            'Preset 18' : (0x01, 0x02), 
            'Preset 19' : (0x02, 0x02), 
            'Preset 20' : (0x03, 0x02), 
            'Preset 21' : (0x0a, 0x02), 
            'Preset 22' : (0x0b, 0x02), 
            'Preset 23' : (0x0c, 0x02), 
            'Preset 24' : (0x0d, 0x02), 
            'Preset 25' : (0x00, 0x03), 
            'Preset 26' : (0x01, 0x03), 
            'Preset 27' : (0x02, 0x03), 
            'Preset 28' : (0x03, 0x03), 
            'Preset 29' : (0x0a, 0x03), 
            'Preset 30' : (0x0b, 0x03), 
            'Preset 31' : (0x0c, 0x03), 
            'Preset 32' : (0x0d, 0x03)
        }
        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds', '13 seconds',
                          '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds', '19 seconds',
                          '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds', '25 seconds',
                          '26 seconds', '27 seconds', '28 seconds', '29 seconds', '30 seconds', '31 seconds',
                          '32 seconds', '33 seconds', '34 seconds', '35 seconds', '36 seconds', '37 seconds',
                          '38 seconds', '39 seconds', '40 seconds', '41 seconds', '42 seconds', '43 seconds',
                          '44 seconds', '45 seconds', '46 seconds', '47 seconds', '48 seconds', '49 seconds',
                          '50 seconds', '51 seconds', '52 seconds', '53 seconds', '54 seconds', '55 seconds',
                          '56 seconds', '57 seconds', '58 seconds', '59 seconds',
                          '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '6 minutes', '7 minutes',
                          '8 minutes', '9 minutes', '10 minutes', '11 minutes', '12 minutes', '13 minutes',
                          '14 minutes', '15 minutes', '16 minutes', '17 minutes', '18 minutes', '19 minutes',
                          '20 minutes')

        area = qualifier['Area']
        if area == 'All':
            area = 0
        fadetime = qualifier['Fade Time']
        preset = qualifier['Preset']

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and fadetime in FadeTimeStates:
                # Compute for Fade Time
                fade = int(fadetime.split()[0])
                if 'second' in fadetime:
                    fade *= 50  # 50 == 1 second
                else:
                    fade *= 3000  # 3000 == 1 minute

                fade_low = fade & 0xFF
                fade_high = fade >> 8

                # Compute for Checksum
                chksum = 0x1c + area + fade_low + ValueStateValues[preset][0] + fade_high + ValueStateValues[preset][1] + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                ClassicPresetCmdString = pack('>8B', 0x1c, area, fade_low, ValueStateValues[preset][0], fade_high, ValueStateValues[preset][1], 0xFF, chksum)
                self.__SetHelper('ClassicPreset', ClassicPresetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetClassicPreset')

    def SetExecutiveMode(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        ValueStateValues = {
            'On'  : 0x15, 
            'Off' : 0x16
        }
        area = qualifier['Area']
        if area == 'All':
            area = 0

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max']:
                # Compute for Checksum
                chksum = 0x1c + area + ValueStateValues[value] + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                ExecutiveModeCmdString = pack('>8B', 0x1c, area, 0x00, ValueStateValues[value], 0x00, 0x00, 0xFF, chksum)
                self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetExecutiveMode')

    def SetFadeArea(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        LevelConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds', '13 seconds',
                          '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds', '19 seconds',
                          '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds', '25 seconds',
                          '26 seconds', '27 seconds', '28 seconds', '29 seconds', '30 seconds', '31 seconds',
                          '32 seconds', '33 seconds', '34 seconds', '35 seconds', '36 seconds', '37 seconds',
                          '38 seconds', '39 seconds', '40 seconds', '41 seconds', '42 seconds', '43 seconds',
                          '44 seconds', '45 seconds', '46 seconds', '47 seconds', '48 seconds', '49 seconds',
                          '50 seconds', '51 seconds', '52 seconds', '53 seconds', '54 seconds', '55 seconds',
                          '56 seconds', '57 seconds', '58 seconds', '59 seconds',
                          '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '6 minutes', '7 minutes',
                          '8 minutes', '9 minutes', '10 minutes', '11 minutes', '12 minutes', '13 minutes',
                          '14 minutes', '15 minutes', '16 minutes', '17 minutes', '18 minutes', '19 minutes',
                          '20 minutes')

        area = qualifier['Area']
        if area == 'All':
            area = 0
        lvl = qualifier['Level']
        fadetime = qualifier['Fade Time']

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if (AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and
                    LevelConstraints['Min'] <= lvl <= LevelConstraints['Max'] and
                    fadetime in FadeTimeStates):
                # Compute for Level
                if lvl == 0:
                    lvl_to_fade = 0xFF
                elif lvl == 100:
                    lvl_to_fade = 0x01
                else:
                    lvl_to_fade = int(hex(round((255 - ((255*lvl)/ 101)) + 1)),16)

                # Compute for Fade Time
                fade = int(fadetime.split()[0])
                if 'second' in fadetime:
                    fade *= 50  # 50 == 1 second
                else:
                    fade *= 3000  # 3000 == 1 minute

                fade_low = fade & 0xFF
                fade_high = fade >> 8

                # Compute for Checksum
                chksum = 0x1c + area + pack('>H', lvl_to_fade)[1] + 0x79 + fade_low + fade_high + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                FadeAreaCmdString = pack('>8B', 0x1c, area, pack('>H', lvl_to_fade)[1], 0x79, fade_low, fade_high, 0xFF, chksum)
                self.__SetHelper('FadeArea', FadeAreaCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFadeArea')

    def SetFadeChannel(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        LevelConstraints = {
            'Min' : 0,
            'Max' : 100
        }
        ChannelOffsetStates = {
            '1'  : (0x80, 0xFF), 
            '2'  : (0x81, 0xFF), 
            '3'  : (0x82, 0xFF), 
            '4'  : (0x83, 0xFF), 
            '5'  : (0x80, 0x00), 
            '6'  : (0x81, 0x00), 
            '7'  : (0x82, 0x00), 
            '8'  : (0x83, 0x00), 
            '9'  : (0x80, 0x01), 
            '10' : (0x81, 0x01), 
            '11' : (0x82, 0x01), 
            '12' : (0x83, 0x01), 
            '13' : (0x80, 0x02), 
            '14' : (0x81, 0x02), 
            '15' : (0x82, 0x02), 
            '16' : (0x83, 0x02), 
        }
        FadeTimeStates = {
            '0 seconds': 0,
            '1 second': 50,
            '2 seconds': 100,
            '3 seconds': 150,
            '4 seconds': 200,
            '5 seconds': 250
        }

        area = qualifier['Area']
        if area == 'All':
            area = 0
        lvl = qualifier['Level']
        ch_offset = qualifier['Channel Offset']
        fadetime = qualifier['Fade Time']

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if (AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and
                    LevelConstraints['Min'] <= lvl <= LevelConstraints['Max'] and
                    fadetime in FadeTimeStates):
                # Compute for Level
                if lvl == 0:
                    lvl_to_fade = 0xFF
                elif lvl == 100:
                    lvl_to_fade = 0x01
                else:
                    lvl_to_fade = int(hex(round((255 - ((255*lvl) / 101)) + 1)), 16)

                # Compute for Checksum
                chksum = 0x1c + area + pack('>H', lvl_to_fade)[1] + ChannelOffsetStates[ch_offset][0] + ChannelOffsetStates[ch_offset][1] + FadeTimeStates[fadetime] + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF    

                FadeChannelCmdString = pack('>8B', 0x1c, area, pack('>H', lvl_to_fade)[1],
                                            ChannelOffsetStates[ch_offset][0], ChannelOffsetStates[ch_offset][1],
                                            FadeTimeStates[fadetime], 0xFF, chksum)
                self.__SetHelper('FadeChannel', FadeChannelCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFadeChannel')

    def SetLinearChannel(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        ChannelConstraints = {
            'Min' : 0,
            'Max' : 255
        }
        ChannelLevelConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds', '13 seconds',
                          '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds', '19 seconds',
                          '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds', '25 seconds',
                          '26 seconds', '27 seconds', '28 seconds', '29 seconds', '30 seconds', '31 seconds',
                          '32 seconds', '33 seconds', '34 seconds', '35 seconds', '36 seconds', '37 seconds',
                          '38 seconds', '39 seconds', '40 seconds', '41 seconds', '42 seconds', '43 seconds',
                          '44 seconds', '45 seconds', '46 seconds', '47 seconds', '48 seconds', '49 seconds',
                          '50 seconds', '51 seconds', '52 seconds', '53 seconds', '54 seconds', '55 seconds',
                          '56 seconds', '57 seconds', '58 seconds', '59 seconds',
                          '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '6 minutes', '7 minutes',
                          '8 minutes', '9 minutes', '10 minutes', '11 minutes', '12 minutes', '13 minutes',
                          '14 minutes', '15 minutes', '16 minutes', '17 minutes', '18 minutes', '19 minutes',
                          '20 minutes')

        area = qualifier['Area']
        if area == 'All':
            area = 0
        channel = qualifier['Channel']
        if channel == 'All':
            channel = 256
        fadetime = qualifier['Fade Time']
        ch_level = qualifier['Channel Level']

        try:
            area = int(area)
            channel = int(channel) - 1   # channel origin is 0
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if (AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and
                    ChannelConstraints['Min'] <= channel <= ChannelConstraints['Max'] and
                    ChannelLevelConstraints['Min'] <= ch_level <= ChannelLevelConstraints['Max'] and
                    fadetime in FadeTimeStates):
                # Compute for Channel Level
                if ch_level == 0:
                    level = 0xFF
                elif ch_level == 100:
                    level = 0x01
                else:
                    level = int(hex(round((255 - ((255 * ch_level) / 101)) + 1)), 16)

                # Compute for Fade Time
                fade = int(fadetime.split()[0])
                if 'second' in fadetime:
                    fade *= 50  # 50 == 1 second
                else:
                    fade *= 3000  # 3000 == 1 minute

                if fade <= 1250:  # 1250 == 25 seconds
                    linearchannelfade = fade // 5  # resolution = 100 ms.
                    OpCode = 0x71
                elif fade <= 9750:  # 9750 == 3 minutes 15 seconds
                    linearchannelfade = fade // 50  # resolution = 1 second
                    OpCode = 0x72
                else:
                    linearchannelfade = fade // 3000  # resolution == 1 minute
                    OpCode = 0x73

                # Compute for Checksum
                chksum = 0x1c + area + channel + OpCode + level + linearchannelfade + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                LinearChannelCmdString = pack('>8B', 0x1c, area, channel, OpCode, level, linearchannelfade, 0xFF, chksum)
                self.__SetHelper('LinearChannel', LinearChannelCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLinearChannel')

    def SetLinearPreset(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        PresetConstraints = {
            'Min': 0,
            'Max': 169
        }
        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds', '13 seconds',
                          '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds', '19 seconds',
                          '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds', '25 seconds',
                          '26 seconds', '27 seconds', '28 seconds', '29 seconds', '30 seconds', '31 seconds',
                          '32 seconds', '33 seconds', '34 seconds', '35 seconds', '36 seconds', '37 seconds',
                          '38 seconds', '39 seconds', '40 seconds', '41 seconds', '42 seconds', '43 seconds',
                          '44 seconds', '45 seconds', '46 seconds', '47 seconds', '48 seconds', '49 seconds',
                          '50 seconds', '51 seconds', '52 seconds', '53 seconds', '54 seconds', '55 seconds',
                          '56 seconds', '57 seconds', '58 seconds', '59 seconds',
                          '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '6 minutes', '7 minutes',
                          '8 minutes', '9 minutes', '10 minutes', '11 minutes', '12 minutes', '13 minutes',
                          '14 minutes', '15 minutes', '16 minutes', '17 minutes', '18 minutes', '19 minutes',
                          '20 minutes')

        area = qualifier['Area']
        if area == 'All':
            area = 0
        fadetime = qualifier['Fade Time']

        try:
            area = int(area)
            preset = int(qualifier['Preset'])
        except:
            self.Discard('Invalid Command')
        else:
            preset -= 1 # preset origin is 0
            if (AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and
                    PresetConstraints['Min'] <= preset <= PresetConstraints['Max'] and
                    fadetime in FadeTimeStates):
                # Compute for Fade Time
                fade = int(fadetime.split()[0])
                if 'second' in fadetime:
                    fade *= 50  # 50 == 1 second
                else:
                    fade *= 3000  # 3000 == 1 minute

                fade_low = fade & 0xFF
                fade_high = fade >> 8

                # Compute Checksum
                chksum = 0x1c + area + preset + 0x65 + fade_low + fade_high + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                LinearPresetCmdString = pack('>8B', 0x1c, area, preset, 0x65, fade_low, fade_high, 0xFF, chksum)
                self.__SetHelper('LinearPreset', LinearPresetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLinearPreset')

    def SetPanic(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds', '13 seconds',
                          '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds', '19 seconds',
                          '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds', '25 seconds',
                          '26 seconds', '27 seconds', '28 seconds', '29 seconds', '30 seconds', '31 seconds',
                          '32 seconds', '33 seconds', '34 seconds', '35 seconds', '36 seconds', '37 seconds',
                          '38 seconds', '39 seconds', '40 seconds', '41 seconds', '42 seconds', '43 seconds',
                          '44 seconds', '45 seconds', '46 seconds', '47 seconds', '48 seconds', '49 seconds',
                          '50 seconds', '51 seconds', '52 seconds', '53 seconds', '54 seconds', '55 seconds',
                          '56 seconds', '57 seconds', '58 seconds', '59 seconds',
                          '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '6 minutes', '7 minutes',
                          '8 minutes', '9 minutes', '10 minutes', '11 minutes', '12 minutes', '13 minutes',
                          '14 minutes', '15 minutes', '16 minutes', '17 minutes', '18 minutes', '19 minutes',
                          '20 minutes')
        ValueStateValues = {
            'On'  : 0x17, 
            'Off' : 0x18
        }

        area = qualifier['Area']
        if area == 'All':
            area = 0
        fadetime = qualifier['Fade Time']

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and fadetime in FadeTimeStates:
                # Compute for Fade Time
                fade = int(fadetime.split()[0])
                if 'second' in fadetime:
                    fade *= 50  # 50 == 1 second
                else:
                    fade *= 3000  # 3000 == 1 minute

                fade_low = fade & 0xFF
                fade_high = fade >> 8

                # Compute for Checksum
                chksum = 0x1c + area + fade_low + ValueStateValues[value] + fade_high + 0x00 + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                PanicCmdString = pack('>8B', 0x1c, area, fade_low, ValueStateValues[value], fade_high, 0x00, 0xFF, chksum)
                self.__SetHelper('Panic', PanicCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPanic')

    def UpdatePresetStatus(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        area = qualifier['Area']
        if area == 'All':
            area = 0

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command for UpdatePresetStatus')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max']:
                chksum = 0x1c + area + 0x63 + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
                PresetStatusCmdString = pack('>8B', 0x1c, area, 0x00, 0x63, 0x00, 0x00, 0xFF, chksum)
                self.__UpdateHelper('PresetStatus', PresetStatusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdatePresetStatus')

    def __MatchPresetStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Preset 1',
              '2': 'Preset 2',
              '3': 'Preset 3',
              '4': 'Preset 4',
              '5': 'Preset 5',
              '6': 'Preset 6',
              '7': 'Preset 7',
              '8': 'Preset 8',
              '9': 'Preset 9',
              '10': 'Preset 10',
              '11': 'Preset 11',
              '12': 'Preset 12',
              '13': 'Preset 13',
              '14': 'Preset 14',
              '15': 'Preset 15',
              '16': 'Preset 16',
              '17': 'Preset 17',
              '18': 'Preset 18',
              '19': 'Preset 19',
              '20': 'Preset 20',
              '21': 'Preset 21',
              '22': 'Preset 22',
              '23': 'Preset 23',
              '24': 'Preset 24',
              '25': 'Preset 25',
              '26': 'Preset 26',
              '27': 'Preset 27',
              '28': 'Preset 28',
              '29': 'Preset 29',
              '30': 'Preset 30',
              '31': 'Preset 31',
              '32': 'Preset 32',
        }

        qualifier = {}
        area = str(unpack('B', match.group(1))[0])
        if area == '0':
            area = 'All'
        qualifier['Area'] = area
        value = ValueStateValues[str(ord(match.group(2).decode()) + 1)]
        self.WriteStatus('PresetStatus', value, qualifier)

    def SetProgramtoCurrentPreset(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }

        area = qualifier['Area']
        if area == 'All':
            area = 0

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max']:                
                # Compute for Checksum
                chksum = 0x1c + area + 0x08 + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                ProgramtoCurrentPresetCmdString = pack('>8B', 0x1c, area, 0x00, 0x08, 0x00, 0x00, 0xFF, chksum)
                self.__SetHelper('ProgramtoCurrentPreset', ProgramtoCurrentPresetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetProgramtoCurrentPreset')

    def SetRecallSavedPreset(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds',
                          '13 seconds', '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds',
                          '19 seconds', '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds',
                          '25 seconds')
        area = qualifier['Area']
        if area == 'All':
            area = 0
        fadetime = qualifier['Fade Time']

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command for SetRecallSavedPreset')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and fadetime in FadeTimeStates:
                fade = int(fadetime.split()[0])
                fade *= 10
                chksum = 0x1c + area + 0x67 + fade + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                RecallSavedPresetCmdString = pack('>8B', 0x1c, area, 0x00, 0x67, 0x00, fade, 0xFF, chksum)
                self.__SetHelper('RecallSavedPreset', RecallSavedPresetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetRecallSavedPreset')

    def SetResetPreset(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        area = qualifier['Area']
        if area == 'All':
            area = 0
        fadetime = qualifier['Fade Time']

        FadeTimeStates = ('0 seconds', '1 second', '2 seconds', '3 seconds', '4 seconds', '5 seconds', '6 seconds',
                          '7 seconds', '8 seconds', '9 seconds', '10 seconds', '11 seconds', '12 seconds', '13 seconds',
                          '14 seconds', '15 seconds', '16 seconds', '17 seconds', '18 seconds', '19 seconds',
                          '20 seconds', '21 seconds', '22 seconds', '23 seconds', '24 seconds', '25 seconds',
                          '26 seconds', '27 seconds', '28 seconds', '29 seconds', '30 seconds', '31 seconds',
                          '32 seconds', '33 seconds', '34 seconds', '35 seconds', '36 seconds', '37 seconds',
                          '38 seconds', '39 seconds', '40 seconds', '41 seconds', '42 seconds', '43 seconds',
                          '44 seconds', '45 seconds', '46 seconds', '47 seconds', '48 seconds', '49 seconds',
                          '50 seconds', '51 seconds', '52 seconds', '53 seconds', '54 seconds', '55 seconds',
                          '56 seconds', '57 seconds', '58 seconds', '59 seconds',
                          '1 minute', '2 minutes', '3 minutes', '4 minutes', '5 minutes', '6 minutes', '7 minutes',
                          '8 minutes', '9 minutes', '10 minutes', '11 minutes', '12 minutes', '13 minutes',
                          '14 minutes', '15 minutes', '16 minutes', '17 minutes', '18 minutes', '19 minutes',
                          '20 minutes')

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and fadetime in FadeTimeStates: 
                # Compute for Fade Time
                fade = int(fadetime.split()[0])
                if 'second' in fadetime:
                    fade *= 50  # 50 == 1 second
                else:
                    fade *= 3000  # 3000 == 1 minute

                fade_low = fade & 0xFF
                fade_high = fade >> 8

                # Compute for Checksum
                chksum = 0x1c + area + fade_low + 0x0F + fade_high + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                ResetPresetCmdString = pack('>8B', 0x1c, area, fade_low, 0x0F, fade_high, 0x00, 0xFF, chksum)
                self.__SetHelper('ResetPreset', ResetPresetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetResetPreset')

    def SetSaveCurrentPreset(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        area = qualifier['Area']
        if area == 'All':
            area = 0

        try:
            area = int(area)
        except (TypeError, ValueError):
            self.Discard('Invalid Command')
        else:
            if AreaConstraints['Min'] <= area <= AreaConstraints['Max']: 
                # Compute for Checksum
                chksum = 0x1c + area + 0x66 + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                SaveCurrentPresetCmdString = pack('>8B', 0x1c, area, 0x00, 0x66, 0x00, 0x00, 0xFF, chksum)
                self.__SetHelper('SaveCurrentPreset', SaveCurrentPresetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetSaveCurrentPreset')

    def SetStopFade(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 255
        }
        ChannelConstraints = {
            'Min': 0,
            'Max': 255
        }

        area = qualifier['Area']
        if area == 'All':
            area = 0
        channel = qualifier['Channel']
        if channel == 'All':
            channel = 256

        try:
            area = int(area)
            channel = int(channel) - 1   # channel origin is 0
        except:
            self.Discard('Invalid Command')
        else:
            if (AreaConstraints['Min'] <= area <= AreaConstraints['Max'] and
                    ChannelConstraints['Min'] <= channel <= ChannelConstraints['Max']):
                # Compute for Checksum
                chksum = 0x1c + area + channel + 0x76 + 0xFF
                chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

                StopFadeCmdString = pack('>8B', 0x1c, area, channel, 0x76, 0x00, 0x00, 0xFF, chksum)
                self.__SetHelper('StopFade', StopFadeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetStopFade')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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
        index = 0    # Start of possible good data

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
