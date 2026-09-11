from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'DefaultPresetRecall': {'Parameters':['MIDI Channel'], 'Status': {}},
            'InputControl': {'Parameters':['MIDI Channel','Number'], 'Status': {}},
            'MasterControl': {'Parameters':['MIDI Channel'], 'Status': {}},
            'MasterMute': {'Parameters':['MIDI Channel'], 'Status': {}},
            'MasterVolume': {'Parameters':['MIDI Channel'], 'Status': {}},
            'MixerControl': {'Parameters':['MIDI Channel','Channel'], 'Status': {}},
            'MixerFade': {'Parameters':['MIDI Channel','Channel'], 'Status': {}},
            'MixerInputMute': {'Parameters':['MIDI Channel','Number'], 'Status': {}},
            'MixerInputVolume': {'Parameters':['MIDI Channel','Number'], 'Status': {}},
            'MixerMute': {'Parameters':['MIDI Channel','Channel'], 'Status': {}},
            'PresetRecall': {'Parameters':['MIDI Channel'], 'Status': {}},
            'PresetSave': {'Parameters':['MIDI Channel'], 'Status': {}},
            }

        self.MIDIChannelStates = {str(midi) : midi - 1 for midi in range(1, 17)}
        
        self.ChannelStates = {str(channel) : channel - 1 for channel in range(1, 33)}
        self.audioTable = [None for i in range (0,200)]
        self.audioTable[0] = 0x00        # - InfdB
        self.audioTable[1] = 0x00        # - InfdB
        self.audioTable[2] = 0x00        # - 138dB
        self.audioTable[3] = 0x10        # - 138dB
        self.audioTable[4] = 0x00        # - 132dB
        self.audioTable[5] = 0x30        # - 132dB
        self.audioTable[6] = 0x00        # - 126dB
        self.audioTable[7] = 0x50        # - 126dB
        self.audioTable[8] = 0x00        # - 120dB
        self.audioTable[9] = 0x70        # - 120dB
        self.audioTable[10] = 0x01        # - 117dB
        self.audioTable[11] = 0x00        # - 117dB
        self.audioTable[12] = 0x01        # - 111dB
        self.audioTable[13] = 0x20        # - 111dB
        self.audioTable[14] = 0x01        # - 108dB
        self.audioTable[15] = 0x30        # - 108dB
        self.audioTable[16] = 0x01        # - 105dB
        self.audioTable[17] = 0x40        # - 105dB
        self.audioTable[18] = 0x01        # - 102dB
        self.audioTable[19] = 0x50        # - 102dB
        self.audioTable[20] = 0x01        # - 99dB
        self.audioTable[21] = 0x60        # - 99dB
        self.audioTable[22] = 0x01        # - 96dB
        self.audioTable[23] = 0x70        # - 96dB
        self.audioTable[24] = 0x02        # - 94dB
        self.audioTable[25] = 0x10        # - 94dB
        self.audioTable[26] = 0x02        # - 92dB
        self.audioTable[27] = 0x30        # - 92dB
        self.audioTable[28] = 0x02        # - 90dB
        self.audioTable[29] = 0x50        # - 90dB
        self.audioTable[30] = 0x02        # - 88dB
        self.audioTable[31] = 0x70        # - 88dB
        self.audioTable[32] = 0x03        # - 86dB
        self.audioTable[33] = 0x10        # - 86dB
        self.audioTable[34] = 0x03        # - 84dB
        self.audioTable[35] = 0x30        # - 84dB
        self.audioTable[36] = 0x03        # - 82dB
        self.audioTable[37] = 0x50        # - 82dB
        self.audioTable[38] = 0x03        # - 80dB
        self.audioTable[39] = 0x70        # - 80dB
        self.audioTable[40] = 0x04        # - 78dB
        self.audioTable[41] = 0x10        # - 78dB
        self.audioTable[42] = 0x05        # - 76dB
        self.audioTable[43] = 0x30        # - 76dB
        self.audioTable[44] = 0x06        # - 74dB
        self.audioTable[45] = 0x50        # - 74dB
        self.audioTable[46] = 0x07        # - 72dB
        self.audioTable[47] = 0x70        # - 72dB
        self.audioTable[48] = 0x09        # - 70dB
        self.audioTable[49] = 0x10        # - 70dB
        self.audioTable[50] = 0x0A        # - 68dB
        self.audioTable[51] = 0x30        # - 68dB
        self.audioTable[52] = 0x0B        # - 66dB
        self.audioTable[53] = 0x50        # - 66dB
        self.audioTable[54] = 0x0C        # - 64dB
        self.audioTable[55] = 0x70        # - 64dB
        self.audioTable[56] = 0x0E        # - 62dB
        self.audioTable[57] = 0x10        # - 62dB
        self.audioTable[58] = 0x0F        # - 60dB
        self.audioTable[59] = 0x30        # - 60dB
        self.audioTable[60] = 0x10        # - 59dB
        self.audioTable[61] = 0x00        # - 59dB
        self.audioTable[62] = 0x10        # - 58dB
        self.audioTable[63] = 0x50        # - 58dB
        self.audioTable[64] = 0x11        # - 57dB
        self.audioTable[65] = 0x20        # - 57dB
        self.audioTable[66] = 0x11        # - 56dB
        self.audioTable[67] = 0x70        # - 56dB
        self.audioTable[68] = 0x12        # - 55dB
        self.audioTable[69] = 0x40        # - 55dB
        self.audioTable[70] = 0x13        # - 54dB
        self.audioTable[71] = 0x10        # - 54dB
        self.audioTable[72] = 0x13        # - 53dB
        self.audioTable[73] = 0x60        # - 53dB
        self.audioTable[74] = 0x14        # - 52dB
        self.audioTable[75] = 0x30        # - 52dB
        self.audioTable[76] = 0x15        # - 51dB
        self.audioTable[77] = 0x00        # - 51dB
        self.audioTable[78] = 0x15        # - 50dB
        self.audioTable[79] = 0x50        # - 50dB
        self.audioTable[80] = 0x16        # - 49dB
        self.audioTable[81] = 0x20        # - 49dB
        self.audioTable[82] = 0x16        # - 48dB
        self.audioTable[83] = 0x70        # - 48dB
        self.audioTable[84] = 0x17        # - 47dB
        self.audioTable[85] = 0x40        # - 47dB
        self.audioTable[86] = 0x18        # - 46dB
        self.audioTable[87] = 0x10        # - 46dB
        self.audioTable[88] = 0x18        # - 45dB
        self.audioTable[89] = 0x60        # - 45dB
        self.audioTable[90] = 0x19        # - 44dB
        self.audioTable[91] = 0x30        # - 44dB
        self.audioTable[92] = 0x1A        # - 43dB
        self.audioTable[93] = 0x00        # - 43dB
        self.audioTable[94] = 0x1A        # - 42dB
        self.audioTable[95] = 0x50        # - 42dB
        self.audioTable[96] = 0x1B        # - 41dB
        self.audioTable[97] = 0x20        # - 41dB
        self.audioTable[98] = 0x1B        # - 40dB
        self.audioTable[99] = 0x70        # - 40dB
        self.audioTable[100] = 0x1D        # - 39dB
        self.audioTable[101] = 0x10        # - 39dB
        self.audioTable[102] = 0x1E        # - 38dB
        self.audioTable[103] = 0x30        # - 38dB
        self.audioTable[104] = 0x1F        # - 37dB
        self.audioTable[105] = 0x50        # - 37dB
        self.audioTable[106] = 0x20        # - 36dB
        self.audioTable[107] = 0x70        # - 36dB
        self.audioTable[108] = 0x22        # - 35dB
        self.audioTable[109] = 0x10        # - 35dB
        self.audioTable[110] = 0x23        # - 34dB
        self.audioTable[111] = 0x30        # - 34dB
        self.audioTable[112] = 0x24        # - 33dB
        self.audioTable[113] = 0x50        # - 33dB
        self.audioTable[114] = 0x25        # - 32dB
        self.audioTable[115] = 0x70        # - 32dB
        self.audioTable[116] = 0x27        # - 31dB
        self.audioTable[117] = 0x10        # - 31dB
        self.audioTable[118] = 0x28        # - 30dB
        self.audioTable[119] = 0x30        # - 30dB
        self.audioTable[120] = 0x29        # - 29dB
        self.audioTable[121] = 0x50        # - 29dB
        self.audioTable[122] = 0x2A        # - 28dB
        self.audioTable[123] = 0x70        # - 28dB
        self.audioTable[124] = 0x2C        # - 27dB
        self.audioTable[125] = 0x10        # - 27dB
        self.audioTable[126] = 0x2D        # - 26dB
        self.audioTable[127] = 0x30        # - 26dB
        self.audioTable[128] = 0x2E        # - 25dB
        self.audioTable[129] = 0x50        # - 25dB
        self.audioTable[130] = 0x2F        # - 24dB
        self.audioTable[131] = 0x70        # - 24dB
        self.audioTable[132] = 0x31        # - 23dB
        self.audioTable[133] = 0x10        # - 23dB
        self.audioTable[134] = 0x32        # - 22dB
        self.audioTable[135] = 0x30        # - 22dB
        self.audioTable[136] = 0x33        # - 21dB
        self.audioTable[137] = 0x50        # - 21dB
        self.audioTable[138] = 0x34        # - 20dB
        self.audioTable[139] = 0x70        # - 20dB
        self.audioTable[140] = 0x37        # - 19dB
        self.audioTable[141] = 0x30        # - 19dB
        self.audioTable[142] = 0x39        # - 18dB
        self.audioTable[143] = 0x70        # - 18dB
        self.audioTable[144] = 0x3C        # - 17dB
        self.audioTable[145] = 0x30        # - 17dB
        self.audioTable[146] = 0x3E        # - 16dB
        self.audioTable[147] = 0x70        # - 16dB
        self.audioTable[148] = 0x41        # - 15dB
        self.audioTable[149] = 0x30        # - 15dB
        self.audioTable[150] = 0x43        # - 14dB
        self.audioTable[151] = 0x70        # - 14dB
        self.audioTable[152] = 0x46        # - 13dB
        self.audioTable[153] = 0x30        # - 13dB
        self.audioTable[154] = 0x48        # - 12dB
        self.audioTable[155] = 0x70        # - 12dB
        self.audioTable[156] = 0x4B        # - 11dB
        self.audioTable[157] = 0x30        # - 11dB
        self.audioTable[158] = 0x4D        # - 10dB
        self.audioTable[159] = 0x70        # - 10dB
        self.audioTable[160] = 0x50        # - 9dB
        self.audioTable[161] = 0x30        # - 9dB
        self.audioTable[162] = 0x52        # - 8dB
        self.audioTable[163] = 0x70        # - 8dB
        self.audioTable[164] = 0x55        # - 7dB
        self.audioTable[165] = 0x30        # - 7dB
        self.audioTable[166] = 0x57        # - 6dB
        self.audioTable[167] = 0x70        # - 6dB
        self.audioTable[168] = 0x5A        # - 5dB
        self.audioTable[169] = 0x30        # - 5dB
        self.audioTable[170] = 0x5C        # - 4dB
        self.audioTable[171] = 0x70        # - 4dB
        self.audioTable[172] = 0x5F        # - 3dB
        self.audioTable[173] = 0x30        # - 3dB
        self.audioTable[174] = 0x61        # - 2dB
        self.audioTable[175] = 0x70        # - 2dB
        self.audioTable[176] = 0x64        # - 1dB
        self.audioTable[177] = 0x30        # - 1dB
        self.audioTable[178] = 0x66        # + 0dB
        self.audioTable[179] = 0x70        # + 0dB
        self.audioTable[180] = 0x69        # + 1dB
        self.audioTable[181] = 0x30        # + 1dB
        self.audioTable[182] = 0x6B        # + 2dB
        self.audioTable[183] = 0x70        # + 2dB
        self.audioTable[184] = 0x6E        # + 3dB
        self.audioTable[185] = 0x30        # + 3dB
        self.audioTable[186] = 0x70        # + 4dB
        self.audioTable[187] = 0x70        # + 4dB
        self.audioTable[188] = 0x73        # + 5dB
        self.audioTable[189] = 0x30        # + 5dB
        self.audioTable[190] = 0x76        # + 6dB
        self.audioTable[191] = 0x70        # + 6dB
        self.audioTable[192] = 0x78        # + 7dB
        self.audioTable[193] = 0x30        # + 7dB
        self.audioTable[194] = 0x7A        # + 8dB
        self.audioTable[195] = 0x70        # + 8dB
        self.audioTable[196] = 0x7D        # + 9dB
        self.audioTable[197] = 0x30        # + 9dB
        self.audioTable[198] = 0x7F        # + MaxdB
        self.audioTable[199] = 0x7F        # + MaxdB

    def SetDefaultPresetRecall(self, value, qualifier):

        midi_chnl = qualifier['MIDI Channel']
        if midi_chnl in self.MIDIChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 16)
            DefaultPresetRecallCmdString = b''.join([b'\xF0\x43', MIDI_Channel, b'\x3E\x12\x00\x4C\x69\x62\x52\x63\x6C\x5F\x5F\x53\x43\x45\x4E\x45\x5F\x5F\x5F\x00\x00\x04\x00\xF7'])
            self.__SetHelper('DefaultPresetRecall', DefaultPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDefaultPresetRecall')

    def SetInputControl(self, value, qualifier):

        NumberStates = {
            '1' : b'\x40', 
            '2' : b'\x42', 
            '3' : b'\x44', 
            '4' : b'\x46'
        }

        ValueStateValues = {
            'Cue' : b'\x01', 
            'Off' : b'\x00'
        }
        
        midi_chnl = qualifier['MIDI Channel']
        number_val = qualifier['Number']
        if midi_chnl in self.MIDIChannelStates and number_val in NumberStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 16)
            InputControlCmdString = b''.join([b'\xF0\x43', MIDI_Channel, b'\x3E\x12\x01\x01\x5E\x00\x00\x00', NumberStates[number_val], 
                                                b'\x00\x00\x00\x00', ValueStateValues[value], b'\xF7'])
            self.__SetHelper('InputControl', InputControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputControl')

    def SetMasterControl(self, value, qualifier):

        ValueStateValues = {
            'Cue' : b'\x01', 
            'Off' : b'\x00'
        }
        
        midi_chnl = qualifier['MIDI Channel']
        if midi_chnl in self.MIDIChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 16)
            MasterControlCmdString = b''.join([b'\xF0\x43', MIDI_Channel, b'\x3E\x12\x01\x01\x61\x00\x00\x00\x00\x00\x00\x00\x00', 
                                                ValueStateValues[value], b'\xF7'])
            self.__SetHelper('MasterControl', MasterControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterControl')

    def SetMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x00\x26\x00', 
            'Off' : b'\x7F\x26\x7F'
        }
        
        midi_chnl = qualifier['MIDI Channel']
        if midi_chnl in self.MIDIChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 176)
            MasterMuteCmdString = b''.join([MIDI_Channel, b'\x62\x32\x63\x0C\x06', ValueStateValues[value]])
            self.__SetHelper('MasterMute', MasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterMute')

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -90,
            'Max' : 9
            }

        midi_chnl = qualifier['MIDI Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and midi_chnl in self.MIDIChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 176)
            index = (value + 90) * 2
            AudioValue1 = pack('B', self.audioTable[index])
            AudioValue2 = pack('B', self.audioTable[index + 1])
            
            MasterVolumeCmdString = b''.join([MIDI_Channel, b'\x62\x7C\x63\x00\x06', AudioValue1, b'\x26', AudioValue2])
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def SetMixerControl(self, value, qualifier):

        ValueStateValues = {
            'Cue' : b'\x01', 
            'Off' : b'\x00'
        }
        
        midi_chnl = qualifier['MIDI Channel']
        channel_val = qualifier['Channel']
        if midi_chnl in self.MIDIChannelStates and channel_val in self.ChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 16)
            Channel_No = pack('B', self.ChannelStates[channel_val])
            MixerControlCmdString = b''.join([b'\xF0\x43', MIDI_Channel, b'\x3E\x12\x01\x01\x5E\x00\x00\x00', Channel_No,
                                                b'\x00\x00\x00\x00', ValueStateValues[value], b'\xF7'])
            self.__SetHelper('MixerControl', MixerControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerControl')

    def SetMixerFade(self, value, qualifier):

        ValueConstraints = {
            'Min' : -90,
            'Max' : 9
            }

        midi_chnl = qualifier['MIDI Channel']
        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and midi_chnl in self.MIDIChannelStates and channel_val in self.ChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 176)
            Channel_No = pack('B', self.ChannelStates[channel_val])
            index = (value + 90) * 2
            AudioValue1 = pack('B', self.audioTable[index])
            AudioValue2 = pack('B', self.audioTable[index + 1])
            MixerFadeCmdString = b''.join([MIDI_Channel, b'\x62', Channel_No, b'\x63\x00\x06', AudioValue1, b'\x26', AudioValue2])
            self.__SetHelper('MixerFade', MixerFadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerFade')

    def SetMixerInputMute(self, value, qualifier):

        NumberStates = {
            '1' : b'\x66', 
            '2' : b'\x68', 
            '3' : b'\x6A', 
            '4' : b'\x6C'
        }

        ValueStateValues = {
            'On'  : b'\x00\x26\x00', 
            'Off' : b'\x7F\x26\x7F'
        }
        
        midi_chnl = qualifier['MIDI Channel']
        number_val = qualifier['Number']
        if midi_chnl in self.MIDIChannelStates and number_val in NumberStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 176)

            MixerInputMuteCmdString = b''.join([MIDI_Channel, b'\x62', NumberStates[number_val], b'\x63\x0B\x06', ValueStateValues[value]])
            self.__SetHelper('MixerInputMute', MixerInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerInputMute')

    def SetMixerInputVolume(self, value, qualifier):

        NumberStates = {
            '1' : b'\x30', 
            '2' : b'\x32', 
            '3' : b'\x34', 
            '4' : b'\x37'
        }

        ValueConstraints = {
            'Min' : -90,
            'Max' : 9
            }

        midi_chnl = qualifier['MIDI Channel']
        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and midi_chnl in self.MIDIChannelStates and number_val in NumberStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 176)
            index = (value + 90) * 2
            AudioValue1 = pack('B', self.audioTable[index])
            AudioValue2 = pack('B', self.audioTable[index + 1])
            
            MixerInputVolumeCmdString = b''.join([MIDI_Channel, b'\x62', NumberStates[number_val], b'\x63\x00\x06', AudioValue1, b'\x26', AudioValue2])
            self.__SetHelper('MixerInputVolume', MixerInputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerInputVolume')
        

    def SetMixerMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x00\x26\x00', 
            'Off' : b'\x7F\x26\x7F'
        }
        
        midi_chnl = qualifier['MIDI Channel']
        channel_val = qualifier['Channel']
        if midi_chnl in self.MIDIChannelStates and channel_val in self.ChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 176)
            Channel_No = pack('B', self.ChannelStates[channel_val] + 54)
            MixerMuteCmdString = b''.join([MIDI_Channel, b'\x62', Channel_No, b'\x63\x0B\x06', ValueStateValues[value]])
            self.__SetHelper('MixerMute', MixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerMute')

    def SetPresetRecall(self, value, qualifier):

        midi_chnl = qualifier['MIDI Channel']
        if 1 <= value <= 300 and midi_chnl in self.MIDIChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 16)
            
            if 1 <= value <= 127:
                presetValue = pack('>H', value)
            elif 128 <= value <= 255:
                presetValue = pack('>H', value + 128)
            else: # 256 <= value <= 300
                presetValue = pack('>H', value + 256)
            
            PresetRecallCmdString = b''.join([b'\xF0\x43', MIDI_Channel, b'\x3E\x12\x00\x4C\x69\x62\x52\x63\x6C\x5F\x5F\x53\x43\x45\x4E\x45\x5F\x5F\x5F', presetValue, b'\x04\x00\xF7'])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        midi_chnl = qualifier['MIDI Channel']
        if 1 <= value <= 300 and midi_chnl in self.MIDIChannelStates:
            MIDI_Channel = pack('B', self.MIDIChannelStates[midi_chnl] + 16)
            
            if 1 <= value <= 127:
                presetValue = pack('>H', value)
            elif 128 <= value <= 255:
                presetValue = pack('>H', value + 128)
            else: # 256 <= value <= 300
                presetValue = pack('>H', value + 256)
                
            PresetSaveCmdString = b''.join([b'\xF0\x43', MIDI_Channel, b'\x3E\x12\x00\x4C\x69\x62\x53\x74\x72\x5F\x5F\x53\x43\x45\x4E\x45\x5F\x5F\x5F', presetValue, b'\x04\x00\xF7'])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
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