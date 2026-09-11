from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.MIDIChannel = '1'
        self.Models = {
            'QU-16': self.ah_qu16,
            'QU-32': self.ah_qu32,
            'QU-24': self.ah_qu24,
            'QU-Pac': self.ah_qu32,
            'QU-SB': self.ah_qu32,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DCAFaderLevel': {'Parameters': ['DCA'], 'Status': {}},
            'DCAMute': {'Parameters': ['DCA'], 'Status': {}},
            'FXFaderLevel': {'Parameters': ['FX Number', 'FX Type'], 'Status': {}},
            'FXMute': {'Parameters': ['FX Number', 'FX Type'], 'Status': {}},
            'InputLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'MasterMute': {'Status': {}},
            'MasterVolumeLevel': {'Status': {}},
            'MixAssign': {'Parameters': ['Input', 'Mix'], 'Status': {}},
            'MixFader': {'Parameters': ['Mix'], 'Status': {}},
            'MixMute': {'Parameters': ['Mix'], 'Status': {}},
            'MMCTransportControl':{'Status': {}},
            'MuteGroup': {'Parameters': ['Group'], 'Status': {}},
            'RemoteShutdown': {'Status': {}},
            'SceneRecall': {'Status': {}},
            'SendLevel': {'Parameters': ['Input', 'Mix'], 'Status': {}},
            }        
        self.LevelStates = {
            10: 0x7F,
            9: 0x7D,
            8: 0x7A,
            7: 0x78,
            6: 0x74,
            5: 0x73,
            4: 0x6F,
            3: 0x6C,
            2: 0x69,
            1: 0x65,
            0: 0x62,
           -1: 0x5E,
           -2: 0x5A,
           -3: 0x56,
           -4: 0x52,
           -5: 0x4E,
           -6: 0x4B,
           -7: 0x48,
           -8: 0x45,
           -9: 0x41,
           -10: 0x3E,
           -11: 0x3C,
           -12: 0x3B,
           -13: 0x39,
           -14: 0x38,
           -15: 0x36,
           -16: 0x34,
           -17: 0x33,
           -18: 0x31,
           -19: 0x30,
           -20: 0x2F,
           -21: 0x2D,
           -22: 0x2B,
           -23: 0x29,
           -24: 0x28,
           -25: 0x26,
           -26: 0x25,
           -27: 0x24,
           -28: 0x22,
           -29: 0x20,
           -30: 0x1F,
           -31: 0x1D,
           -32: 0x1B,
           -33: 0x1A,
           -34: 0x18,
           -35: 0x17,
           -36: 0x15,
           -37: 0x13,
           -38: 0x12,
           -39: 0x11,
           -40: 0x10,
           -41: 0x0F,
           -42: 0x0E,
           -43: 0x0D,
           -44: 0x0C,
           -45: 0x0B,
           -46: 0x0A,
           -47: 0x09,
           -48: 0x04,
           -49: 0x02,
           -50: 0x00
        }

        self.LevelValues = {
            0x7F: 10,
            0x7E: 9,
            0x7D: 9,
            0x7C: 8,
            0x7B: 8,
            0x7A: 8,
            0x79: 8,
            0x78: 7,
            0x77: 7,
            0x76: 7,
            0x75: 7,
            0x74: 6,
            0x73: 5,
            0x72: 4,
            0x71: 4,
            0x70: 4,
            0x6F: 4,
            0x6E: 3,
            0x6D: 3,
            0x6C: 3,
            0x6B: 2,
            0x6A: 2,
            0x69: 2,
            0x68: 1,
            0x67: 1,
            0x66: 1,
            0x65: 1,
            0x64: 0,
            0x63: 0,
            0x62: 0,
            0x61: -1,
            0x60: -1,
            0x5F: -1,
            0x5E: -1,
            0x5D: -2,
            0x5C: -2,
            0x5B: -2,
            0x5A: -2,
            0x59: -3,
            0x58: -3,
            0x57: -3,
            0x56: -3,
            0x55: -4,
            0x54: -4,
            0x53: -4,
            0x52: -4,
            0x51: -5,
            0x50: -5,
            0x4F: -5,
            0x4E: -5,
            0x4D: -6,
            0x4C: -6,
            0x4B: -6,
            0x4A: -7,
            0x49: -7,
            0x48: -7,
            0x47: -8,
            0x46: -8,
            0x45: -8,
            0x44: -9,
            0x43: -9,
            0x42: -9,
            0x41: -9,
            0x40: -10,
            0x3F: -10,
            0x3E: -10,
            0x3D: -11,
            0x3C: -11,
            0x3B: -12,
            0x3A: -12,
            0x39: -13,
            0x38: -14,
            0x37: -15,
            0x36: -15,
            0x35: -16,
            0x34: -16,
            0x33: -17,
            0x32: -18,
            0x31: -18,
            0x30: -19,
            0x2F: -20,
            0x2E: -21,
            0x2D: -21,
            0x2C: -22,
            0x2B: -22,
            0x2A: -23,
            0x29: -23,
            0x28: -24,
            0x27: -25,
            0x26: -25,
            0x25: -26,
            0x24: -27,
            0x23: -28,
            0x22: -28,
            0x21: -29,
            0x20: -29,
            0x1F: -30,
            0x1E: -31,
            0x1D: -31,
            0x1C: -32,
            0x1B: -32,
            0x1A: -33,
            0x19: -34,
            0x18: -34,
            0x17: -35,
            0x16: -36,
            0x15: -36,
            0x14: -37,
            0x13: -37,
            0x12: -38,
            0x11: -39,
            0x10: -40,
            0x0F: -41,
            0x0E: -42,
            0x0D: -43,
            0x0C: -44,
            0x0B: -45,
            0x0A: -46,
            0x09: -47,
            0x08: -48,
            0x07: -48,
            0x06: -48,
            0x05: -48,
            0x04: -48,
            0x03: -49,
            0x02: -49,
            0x01: -49,
            0x00: -50
        }

        self.Volume_regex = re.compile(b'([\xB0-\xBF])\x63([\x00-\x3F]|[\x50-\x6D])[\xB0-\xBF]\x62\x17[\xB0-\xBF]\x06([\x00-\x7F])[\xB0-\xBF]\x26\x07')
        self.MixAssign_regex = re.compile(b'([\xB0-\xBF])\x63([\x00-\x3F]|[\x50-\x6D])[\xB0-\xBF]\x62\x55[\xB0-\xBF]\x06([\x00-\x7F])[\xB0-\xBF]\x26([\x00-\x13])')
        self.SendLevel_regex = re.compile(b'([\xB0-\xBF])\x63([\x00-\x3F]|[\x50-\x6D])[\xB0-\xBF]\x62\x20[\xB0-\xBF]\x06([\x00-\x7F])[\xB0-\xBF]\x26([\x00-\x13])')
        self.Mute_regex = re.compile(b'([\x90-\x9F])([\x00-\x3F]|[\x50-\x6D])([\x3F\x7F])')  
        
    @property
    def MIDIChannel(self):
        return self._MIDIChannel

    @MIDIChannel.setter
    def MIDIChannel(self, value):
        self.MidiChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            '11': 'A',
            '12': 'B',
            '13': 'C',
            '14': 'D',
            '15': 'E',
            '16': 'F'
        }
        if 1 <= int(value) <= 16:
            self._MIDIChannel = self.MidiChannelStates[value]

    def SetDCAFaderLevel(self, value, qualifier):

        DCAStates = {
            '1': 0x10,
            '2': 0x11,
            '3': 0x12,
            '4': 0x13,
            }

        ValueConstraints = {
            'Min': -50,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MidiConversion = int('B' + self._MIDIChannel, 16)
            DCAFaderLevelCmdString = pack('BBBBBBBBBBBB', MidiConversion, 0x63, DCAStates[qualifier['DCA']], MidiConversion, 0x62, 0x17, MidiConversion, 0x06, self.LevelStates[value], MidiConversion, 0x26, 0x07)
            self.__SetHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAFaderLevel')
    
    def UpdateDCAFaderLevel(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetDCAMute(self, value, qualifier):

        DCAStates = {
            '1': 0x10,
            '2': 0x11,
            '3': 0x12,
            '4': 0x13,
            }

        DCAMuteValues = {
            'On': 0x7F,
            'Off': 0x3F
        }

        MidiConversion1 = int('9' + self._MIDIChannel, 16)
        MidiConversion2 = int('8' + self._MIDIChannel, 16)
        DCAMuteCmdString = pack('>6B', MidiConversion1, DCAStates[qualifier['DCA']], DCAMuteValues[value], MidiConversion2, DCAStates[qualifier['DCA']], 0x00)
        self.__SetHelper('DCAMute', DCAMuteCmdString, value, qualifier)

    def UpdateDCAMute(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetFXFaderLevel(self, value, qualifier):

        FXTypeStates = {
            'Send': 'Low',
            'Return': 'High'
        }

        FXSendStates = {
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03,
            }

        FXReturnStates = {
            '1': 0x08,
            '2': 0x09,
            '3': 0x0A,
            '4': 0x0B,
            }

        ValueConstraints = {
            'Min': -50,
            'Max': 10
            }

        fx_typechoice = FXTypeStates[qualifier['FX Type']]

        if fx_typechoice == 'Low':
            fx_value = FXSendStates[qualifier['FX Number']]
        elif fx_typechoice == 'High':
            fx_value = FXReturnStates[qualifier['FX Number']]

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MidiConversion = int('B' + self._MIDIChannel, 16)
            FXFaderLevelCmdString = pack('BBBBBBBBBBBB', MidiConversion, 0x63, fx_value, MidiConversion, 0x62, 0x17, MidiConversion, 0x06, self.LevelStates[value], MidiConversion, 0x26, 0x07)
            self.__SetHelper('FXFaderLevel', FXFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFXFaderLevel')

    def UpdateFXFaderLevel(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)
    
    def SetFXMute(self, value, qualifier):

        FXTypeStates = {
            'Send': 'Low',
            'Return': 'High'
        }

        FXSendStates = {
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03,
            }

        FXReturnStates = {
            '1': 0x08,
            '2': 0x09,
            '3': 0x0A,
            '4': 0x0B,
            }
        FXMuteValues = {
            'On': 0x7F,
            'Off': 0x3F
        }

        fx_typechoice = FXTypeStates[qualifier['FX Type']]

        if fx_typechoice == 'Low':
            fx_value = FXSendStates[qualifier['FX Number']]
        elif fx_typechoice == 'High':
            fx_value = FXReturnStates[qualifier['FX Number']]

        MidiConversion1 = int('9' + self._MIDIChannel, 16)
        MidiConversion2 = int('8' + self._MIDIChannel, 16)
        FXMuteCmdString = pack('>6B', MidiConversion1, fx_value, FXMuteValues[value], MidiConversion2, fx_value, 0x00)
        self.__SetHelper('FXMute', FXMuteCmdString, value, qualifier)

    def UpdateFXMute(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetInputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -50,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MidiConversion = int('B' + self._MIDIChannel, 16)
            InputCmdString = pack('BBBBBBBBBBBB', MidiConversion, 0x63, self.InputStates[qualifier['Input']], MidiConversion, 0x62, 0x17, MidiConversion, 0x06, self.LevelStates[value], MidiConversion, 0x26, 0x07)
            self.__SetHelper('InputLevel', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x7F,
            'Off': 0x3F
        }
        MidiConversion1 = int('9' + self._MIDIChannel, 16)
        MidiConversion2 = int('8' + self._MIDIChannel, 16)
        InputMuteCmdString = pack('BBBBBB', MidiConversion1, self.InputStates[qualifier['Input']], ValueStateValues[value], MidiConversion2, self.InputStates[qualifier['Input']], 0x00)
        self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        
    def UpdateInputMute(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x7F,
            'Off': 0x3F
        }
        MidiConversion1 = int('9' + self._MIDIChannel, 16)
        MidiConversion2 = int('8' + self._MIDIChannel, 16)
        MasterMuteCmdString = pack('BBBBBB', MidiConversion1, 0x67, ValueStateValues[value], MidiConversion2, 0x67, 0x00)  # customer confirmed channel for master control is 67, per Legacy driver
        self.__SetHelper('MasterMute', MasterMuteCmdString, value, qualifier)

    def UpdateMasterMute(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetMasterVolumeLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -50,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MidiConversion = int('B' + self._MIDIChannel, 16)
            MasterVolumeLevelCmdString = pack('BBBBBBBBBBBB', MidiConversion, 0x63, 0x67, MidiConversion, 0x62, 0x17, MidiConversion, 0x06, self.LevelStates[value], MidiConversion, 0x26, 0x07)
            self.__SetHelper('MasterVolumeLevel', MasterVolumeLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolumeLevel')

    def UpdateMasterVolumeLevel(self, value, qualifier):

        DCANames = {
            0x10: '1',
            0x11: '2',
            0x12: '3',
            0x13: '4'
            }
        FXSendNames = {
            0x00: '1',
            0x01: '2',
            0x02: '3',
            0x03: '4'
            }
        FXReturnNames = {
            0x08: '1',
            0x09: '2',
            0x0A: '3',
            0x0B: '4'
            }
        MuteValues = {
            0x7F: 'On',
            0x3F: 'Off'
        }
        AssignValues = {
            0x01: 'On',
            0x00: 'Off'
        }
        MuteGroupNames = {
            0x50: '1',
            0x51: '2',
            0x52: '3',
            0x53: '4'
            }
        MasterVolumeLevelCmdString = b'\xF0\x00\x00\x1A\x50\x11\x01\x00\x7F\x10\x00\xF7'
        res = self.__UpdateHelper('MasterVolumeLevel', MasterVolumeLevelCmdString, value, qualifier)
        if res:
            try:
                tempList = re.findall(self.Volume_regex, res)
                if tempList:
                    for temp in tempList:
                        midi_channel=temp[0]
                        channel_number=unpack('B', temp[1])[0]
                        level_value=self.LevelValues[unpack('B', temp[2])[0]]
                        if midi_channel == pack('B', int('B' + self._MIDIChannel, 16)):
                            if channel_number == 0x67:  
                                self.WriteStatus('MasterVolumeLevel', level_value, None)
                            elif channel_number in self.InputNames:
                                input_channel=self.InputNames[channel_number]
                                self.WriteStatus('InputLevel', level_value, {'Input': input_channel})
                            elif channel_number in DCANames:
                                dca_channel=DCANames[channel_number]
                                self.WriteStatus('DCAFaderLevel', level_value, {'DCA': dca_channel})
                            elif channel_number in FXSendNames or channel_number in FXReturnNames:
                                if channel_number in FXSendNames:
                                    fx_number=FXSendNames[channel_number]
                                    fx_type='Send'
                                else:
                                    fx_number=FXReturnNames[channel_number]
                                    fx_type='Return'
                                self.WriteStatus('FXFaderLevel', level_value, {'FX Number': fx_number, 'FX Type': fx_type})
                            elif channel_number in self.MixNames:
                                mix_channel=self.MixNames[channel_number]
                                self.WriteStatus('MixFader', level_value, {'Mix': mix_channel})
                else:
                    self.Error(['System level status is unavailable'])
            except (KeyError, ValueError):
                self.Error(['Error occurred when getting system level status'])

            try:
                tempList=re.findall(self.Mute_regex, res)
                if tempList:
                    for temp in tempList:
                        midi_channel=temp[0]
                        channel_number=unpack('B', temp[1])[0]
                        mute_value=MuteValues[unpack('B', temp[2])[0]]
                        if midi_channel == pack('B', int('9' + self._MIDIChannel, 16)):
                            if channel_number == 0x67: 
                                self.WriteStatus('MasterMute', mute_value, qualifier)
                            elif channel_number in self.InputNames:
                                input_channel=self.InputNames[channel_number]
                                self.WriteStatus('InputMute', mute_value, {'Input': input_channel})
                            elif channel_number in DCANames:
                                dca_channel=DCANames[channel_number]
                                self.WriteStatus('DCAMute', mute_value, {'DCA': dca_channel})
                            elif channel_number in FXSendNames or channel_number in FXReturnNames:
                                if channel_number in FXSendNames:
                                    fx_number=FXSendNames[channel_number]
                                    fx_type='Send'
                                else:
                                    fx_number=FXReturnNames[channel_number]
                                    fx_type='Return'
                                self.WriteStatus('FXMute', mute_value, {'FX Number': fx_number, 'FX Type': fx_type})
                            elif channel_number in self.MixNames:
                                mix_channel=self.MixNames[channel_number]
                                self.WriteStatus('MixMute', mute_value, {'Mix': mix_channel})
                            elif channel_number in MuteGroupNames:
                                group=MuteGroupNames[channel_number]
                                self.WriteStatus('MuteGroup', mute_value, {'Group': group})
                else:
                    self.Error(['System mute status is unavailable'])
            except (KeyError, ValueError):
                self.Error(['Error occurred when getting system mute status'])

            try:
                tempList=re.findall(self.MixAssign_regex, res)
                if tempList:
                    for temp in tempList:
                        midi_channel=temp[0]
                        channel_number=unpack('B', temp[1])[0]
                        assign_value=AssignValues[unpack('B', temp[2])[0]]
                        mix_name=self.MixNames2[unpack('B', temp[3])[0]]
                        if midi_channel == pack('B', int('B' + self._MIDIChannel, 16)):
                            if channel_number in self.InputNames:
                                input_name=self.InputNames[channel_number]
                                self.WriteStatus('MixAssign', assign_value, {'Input': input_name, 'Mix': mix_name})
                else:
                    self.Error(['System mix assign status is unavailable'])
            except (KeyError, ValueError):
                self.Error(['Error occurred when getting system mix assign status'])

            try:
                tempList=re.findall(self.SendLevel_regex, res)
                if tempList:
                    for temp in tempList:
                        midi_channel=temp[0]
                        channel_number=unpack('B', temp[1])[0]
                        level_value=self.LevelValues[unpack('B', temp[2])[0]]
                        mix_name=self.MixNames2[unpack('B', temp[3])[0]]
                        if midi_channel == pack('B', int('B' + self._MIDIChannel, 16)):
                            if channel_number in self.InputNames:
                                input_name=self.InputNames[channel_number]
                                self.WriteStatus('SendLevel', level_value, {'Input': input_name, 'Mix': mix_name})
                else:
                    self.Error(['System send level status is unavailable'])
            except (KeyError, ValueError):
                self.Error(['Error occurred when getting system send level status'])

    def SetMixAssign(self, value, qualifier):

        ValueStateValues={
            'On': 0x01,
            'Off': 0x00
        }

        MidiConversion=int('B' + self._MIDIChannel, 16)
        MixAssignCmdString=pack('BBBBBBBBBBBB', MidiConversion, 0x63, self.InputStates[qualifier['Input']], MidiConversion, 0x62, 0x55, MidiConversion, 0x06, ValueStateValues[value], MidiConversion, 0x26, self.MixStates2[qualifier['Mix']])
        self.__SetHelper('MixAssign', MixAssignCmdString, value, qualifier)

    def UpdateMixAssign(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetMixFader(self, value, qualifier):


        ValueConstraints={
            'Min': -50,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MidiConversion=int('B' + self._MIDIChannel, 16)
            MixFaderCmdString=pack('BBBBBBBBBBBB', MidiConversion, 0x63, self.MixStates[qualifier['Mix']], MidiConversion, 0x62, 0x17, MidiConversion, 0x06, self.LevelStates[value], MidiConversion, 0x26, 0x07)
            self.__SetHelper('MixFader', MixFaderCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixFader')

    def UpdateMixFader(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetMixMute(self, value, qualifier):

        MixMuteValues={
            'On': 0x7F,
            'Off': 0x3F
        }

        MidiConversion1=int('9' + self._MIDIChannel, 16)
        MidiConversion2=int('8' + self._MIDIChannel, 16)
        MixMuteCmdString=pack('BBBBBB', MidiConversion1, self.MixStates[qualifier['Mix']], MixMuteValues[value], MidiConversion2, self.MixStates[qualifier['Mix']], 0x00)
        self.__SetHelper('MixMute', MixMuteCmdString, value, qualifier)

    def UpdateMixMute(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetMuteGroup(self, value, qualifier):

        GroupStates={
            '1': 0x50,
            '2': 0x51,
            '3': 0x52,
            '4': 0x53,
        }

        MuteGroupValues={
            'On': 0x7F,
            'Off': 0x3F
        }

        MidiConversion1=int('9' + self._MIDIChannel, 16)
        MidiConversion2=int('8' + self._MIDIChannel, 16)
        MuteGroupCmdString=pack('>6B', MidiConversion1, GroupStates[qualifier['Group']], MuteGroupValues[value], MidiConversion2, GroupStates[qualifier['Group']], 0x00)
        self.__SetHelper('MuteGroup', MuteGroupCmdString, value, qualifier)

    def UpdateMuteGroup(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def SetMMCTransportControl(self, value, qualifier):
        
        ValueStateValues = {
            'Stop'          : 0x01,
            'Play'          : 0x02,
            'Fast Forward'  : 0x04,
            'Rewind'        : 0x05,
            'Record Strobe' : 0x06,
            'Pause'         : 0x09
        }

        MMCTransportControlCmdString = pack('>6B', 0xF0, 0x7F, 0x7F, 0x06, ValueStateValues[value], 0xF7)
        self.__SetHelper('MMCTransportControl', MMCTransportControlCmdString, value, qualifier)        
    
    def SetRemoteShutdown(self, value, qualifier):

        MidiConversion=int('B' + self._MIDIChannel, 16)
        RemoteShutdownCmdString=pack('BBBBBBBBBBBB', MidiConversion, 0x63, 0x00, MidiConversion, 0x62, 0x5F, MidiConversion, 0x06, 0x00, MidiConversion, 0x26, 0x00)
        self.__SetHelper('RemoteShutdown', RemoteShutdownCmdString, value, qualifier)
                
    def SetSceneRecall(self, value, qualifier):

        ValueConstraints={
            'Min': 1,
            'Max': 100
            }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            MidiConversion=int('B' + self._MIDIChannel, 16)
            SceneRecallCmdString=pack('BBBBBBBB', MidiConversion, 0x00, 0x00, MidiConversion, 0x20, 0x00, int('C' + self._MIDIChannel, 16), int(value) - 1)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')
            
    def SetSendLevel(self, value, qualifier):

        ValueConstraints={
            'Min': -50,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MidiConversion=int('B' + self._MIDIChannel, 16)
            SendLevelCmdString=pack('BBBBBBBBBBBB', MidiConversion, 0x63, self.InputStates[qualifier['Input']], MidiConversion, 0x62, 0x20, MidiConversion, 0x06, self.LevelStates[value], MidiConversion, 0x26, self.MixStates2[qualifier['Mix']])
            self.__SetHelper('SendLevel', SendLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSendLevel')

    def UpdateSendLevel(self, value, qualifier):
        self.UpdateMasterVolumeLevel(value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug=True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk=False

            self.counter=self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res=self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x14\xF7')
            if not res:
                return ''
            else:
                return res           

    def OnConnected(self):
        self.connectionFlag=True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter=0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag=False

    def ah_qu16(self):
        self.InputStates={
            '1': 0x20,
            '2': 0x21,
            '3': 0x22,
            '4': 0x23,
            '5': 0x24,
            '6': 0x25,
            '7': 0x26,
            '8': 0x27,
            '9': 0x28,
            '10': 0x29,
            '11': 0x2A,
            '12': 0x2B,
            '13': 0x2C,
            '14': 0x2D,
            '15': 0x2E,
            '16': 0x2F
        }
        self.InputNames={
            0x20: '1',
            0x21: '2',
            0x22: '3',
            0x23: '4',
            0x24: '5',
            0x25: '6',
            0x26: '7',
            0x27: '8',
            0x28: '9',
            0x29: '10',
            0x2A: '11',
            0x2B: '12',
            0x2C: '13',
            0x2D: '14',
            0x2E: '15',
            0x2F: '16'
        }
        self.MixStates={
            '1': 0x60,
            '2': 0x61,
            '3': 0x62,
            '4': 0x63,
            '5-6': 0x64,
            '7-8': 0x65,
            '9-10': 0x66,
            'LR': 0x67
        }
        self.MixNames={
            0x60: '1',
            0x61: '2',
            0x62: '3',
            0x63: '4',
            0x64: '5-6',
            0x65: '7-8',
            0x66: '9-10',
            0x67: 'LR'
        }
        self.MixStates2={
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03,
            '5-6': 0x04,
            '7-8': 0x05,
            '9-10': 0x06,
            'LR': 0x07,
            'FX send 1': 0x10,
            'FX send 2': 0x11
        }
        self.MixNames2={
            0x00: '1',
            0x01: '2',
            0x02: '3',
            0x03: '4',
            0x04: '5-6',
            0x05: '7-8',
            0x06: '9-10',
            0x07: 'LR',
            0x10: 'FX send 1',
            0x11: 'FX send 2'
        }


    def ah_qu24(self):
        self.InputStates={
            '1': 0x20,
            '2': 0x21,
            '3': 0x22,
            '4': 0x23,
            '5': 0x24,
            '6': 0x25,
            '7': 0x26,
            '8': 0x27,
            '9': 0x28,
            '10': 0x29,
            '11': 0x2A,
            '12': 0x2B,
            '13': 0x2C,
            '14': 0x2D,
            '15': 0x2E,
            '16': 0x2F,
            '17': 0x30,
            '18': 0x31,
            '19': 0x32,
            '20': 0x33,
            '21': 0x34,
            '22': 0x35,
            '23': 0x36,
            '24': 0x37,
        }
        self.InputNames={
            0x20: '1',
            0x21: '2',
            0x22: '3',
            0x23: '4',
            0x24: '5',
            0x25: '6',
            0x26: '7',
            0x27: '8',
            0x28: '9',
            0x29: '10',
            0x2A: '11',
            0x2B: '12',
            0x2C: '13',
            0x2D: '14',
            0x2E: '15',
            0x2F: '16',
            0x30: '17',
            0x31: '18',
            0x32: '19',
            0x33: '20',
            0x34: '21',
            0x35: '22',
            0x36: '23',
            0x37: '24'
        }
        self.MixStates={
            '1': 0x60,
            '2': 0x61,
            '3': 0x62,
            '4': 0x63,
            '5-6': 0x64,
            '7-8': 0x65,
            '9-10': 0x66,
            'LR': 0x67,
            'Grp1-2': 0x68,
            'Grp3-4': 0x69,
            'Grp5-6': 0x6A,
            'Grp7-8': 0x6B,
            'MTX1-2': 0x6C,
            'MTX3-4': 0x6D,
        }
        self.MixNames={
            0x60: '1',
            0x61: '2',
            0x62: '3',
            0x63: '4',
            0x64: '5-6',
            0x65: '7-8',
            0x66: '9-10',
            0x67: 'LR',
            0x68: 'Grp1-2',
            0x69: 'Grp3-4',
            0x6A: 'Grp5-6',
            0x6B: 'Grp7-8',
            0x6C: 'MTX1-2',
            0x6D: 'MTX3-4'
        }
        self.MixStates2={
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03,
            '5-6': 0x04,
            '7-8': 0x05,
            '9-10': 0x06,
            'LR': 0x07,
            'Grp1-2': 0x08,
            'Grp3-4': 0x09,
            'Grp5-6': 0x0A,
            'Grp7-8': 0x0B,
            'MTX1-2': 0x0C,
            'MTX3-4': 0x0D,
            'FX send 1': 0x10,
            'FX send 2': 0x11,
            'FX send 3': 0x12,
            'FX send 4': 0x13
        }
        self.MixNames2={
            0x00: '1',
            0x01: '2',
            0x02: '3',
            0x03: '4',
            0x04: '5-6',
            0x05: '7-8',
            0x06: '9-10',
            0x07: 'LR',
            0x08: 'Grp1-2',
            0x09: 'Grp3-4',
            0x0A: 'Grp5-6',
            0x0B: 'Grp7-8',
            0x0C: 'MTX1-2',
            0x0D: 'MTX3-4',
            0x10: 'FX send 1',
            0x11: 'FX send 2',
            0x12: 'FX send 3',
            0x13: 'FX send 4'
        }

    def ah_qu32(self):
        self.InputStates={
            '1': 0x20,
            '2': 0x21,
            '3': 0x22,
            '4': 0x23,
            '5': 0x24,
            '6': 0x25,
            '7': 0x26,
            '8': 0x27,
            '9': 0x28,
            '10': 0x29,
            '11': 0x2A,
            '12': 0x2B,
            '13': 0x2C,
            '14': 0x2D,
            '15': 0x2E,
            '16': 0x2F,
            '17': 0x30,
            '18': 0x31,
            '19': 0x32,
            '20': 0x33,
            '21': 0x34,
            '22': 0x35,
            '23': 0x36,
            '24': 0x37,
            '25': 0x38,
            '26': 0x39,
            '27': 0x3A,
            '28': 0x3B,
            '29': 0x3C,
            '30': 0x3D,
            '31': 0x3E,
            '32': 0x3F
        }
        self.InputNames={
            0x20: '1',
            0x21: '2',
            0x22: '3',
            0x23: '4',
            0x24: '5',
            0x25: '6',
            0x26: '7',
            0x27: '8',
            0x28: '9',
            0x29: '10',
            0x2A: '11',
            0x2B: '12',
            0x2C: '13',
            0x2D: '14',
            0x2E: '15',
            0x2F: '16',
            0x30: '17',
            0x31: '18',
            0x32: '19',
            0x33: '20',
            0x34: '21',
            0x35: '22',
            0x36: '23',
            0x37: '24',
            0x38: '25',
            0x39: '26',
            0x3A: '27',
            0x3B: '28',
            0x3C: '29',
            0x3D: '30',
            0x3E: '31',
            0x3F: '32'
        }
        self.MixStates={
            '1': 0x60,
            '2': 0x61,
            '3': 0x62,
            '4': 0x63,
            '5-6': 0x64,
            '7-8': 0x65,
            '9-10': 0x66,
            'LR': 0x67,
            'Grp1-2': 0x68,
            'Grp3-4': 0x69,
            'Grp5-6': 0x6A,
            'Grp7-8': 0x6B,
            'MTX1-2': 0x6C,
            'MTX3-4': 0x6D,
        }
        self.MixNames={
            0x60: '1',
            0x61: '2',
            0x62: '3',
            0x63: '4',
            0x64: '5-6',
            0x65: '7-8',
            0x66: '9-10',
            0x67: 'LR',
            0x68: 'Grp1-2',
            0x69: 'Grp3-4',
            0x6A: 'Grp5-6',
            0x6B: 'Grp7-8',
            0x6C: 'MTX1-2',
            0x6D: 'MTX3-4'
        }
        self.MixStates2={
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03,
            '5-6': 0x04,
            '7-8': 0x05,
            '9-10': 0x06,
            'LR': 0x07,
            'Grp1-2': 0x08,
            'Grp3-4': 0x09,
            'Grp5-6': 0x0A,
            'Grp7-8': 0x0B,
            'MTX1-2': 0x0C,
            'MTX3-4': 0x0D,
            'FX send 1': 0x10,
            'FX send 2': 0x11,
            'FX send 3': 0x12,
            'FX send 4': 0x13
        }
        self.MixNames2={
            0x00: '1',
            0x01: '2',
            0x02: '3',
            0x03: '4',
            0x04: '5-6',
            0x05: '7-8',
            0x06: '9-10',
            0x07: 'LR',
            0x08: 'Grp1-2',
            0x09: 'Grp3-4',
            0x0A: 'Grp5-6',
            0x0B: 'Grp7-8',
            0x0C: 'MTX1-2',
            0x0D: 'MTX3-4',
            0x10: 'FX send 1',
            0x11: 'FX send 2',
            0x12: 'FX send 3',
            0x13: 'FX send 4'
        }


    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method=getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method=getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command=self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command]={'method': {}}

            Subscribe=self.Subscription[command]
            Method=Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method=Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]]={}
                            Method=Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback']=callback
            Method['qualifier']=qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
            Subscribe=self.Subscription[command]
            Method=Subscribe['method']
            Command=self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method=Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter=0
        if not self.connectionFlag:
            self.OnConnected()
        Command=self.Commands[command]
        Status=Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status=Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]]={}
                        Status=Status[qualifier[Parameter]]
                    else:
                        return
        try:
            if Status['Live'] != value:
                Status['Live']=value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live']=value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command=self.Commands.get(command, None)
        if Command:
            Status=Command['Status']
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Status=Status[qualifier[Parameter]]
                    except KeyError:
                        return None
            try:
                return Status['Live']
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType='Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo='IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
