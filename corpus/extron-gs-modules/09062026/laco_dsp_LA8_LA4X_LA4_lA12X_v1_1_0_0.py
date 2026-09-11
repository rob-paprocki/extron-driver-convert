from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack


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
            'ExecutiveMode': {'Status': {}},
            'Gain': {'Parameters': ['Channel'], 'Status': {}},
            'Impedance': {'Parameters': ['Frequency', 'Value Type', 'Number'], 'Status': {}},
            'InputAandB': {'Status': {}},
            'InputCandD': {'Status': {}},
            'Mute': {'Parameters': ['Channel'], 'Status': {}},
            'PilotToneFrequency': {'Status': {}},
            'PilotToneResolution': {'Status': {}},
            'PilotToneThreshold': {'Status': {}},
            'PowerControl': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'SignalAmplitude': {'Parameters': ['Frequency'], 'Status': {}},
            'SignalFadeTime': {'Parameters': ['Frequency'], 'Status': {}},
            'SignalFrequency': {'Parameters': ['Frequency'], 'Status': {}},
            'SignalGFTSize': {'Parameters': ['Frequency'], 'Status': {}},
            'SignalHoldTime': {'Parameters': ['Frequency'], 'Status': {}},
        }


    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        ExecutiveModeCmdString = b'\x4C\x00\x00\x10\x19\x03\x00\x0A\x00\x0C\x00\x04\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        ExecutiveModeCmdString = b'\x4C\x00\x00\x0C\x18\x03\x00\x0A\x00\x0C\x00\x00'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ChannelStates = {
            '1': b'\x0A',
            '2': b'\x14',
            '3': b'\x1E',
            '4': b'\x28'
        }

        ValueConstraints = {
            'Min': -60,
            'Max': 15
        }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volume = pack('>l', int(value * 10))

            if channel_val == 'All':
                header = b'\x4C\x00\x00\x34'
                ch1 = b'\x19\x03\x00\x78\x00\x0A\x00\x04' + volume
                ch2 = b'\x19\x03\x00\x78\x00\x14\x00\x04' + volume
                ch3 = b'\x19\x03\x00\x78\x00\x1E\x00\x04' + volume
                ch4 = b'\x19\x03\x00\x78\x00\x28\x00\x04' + volume
                GainCmdString = b''.join([header, ch1, ch2, ch3, ch4])
            else:
                GainCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x78\x00', ChannelStates[channel_val], b'\x00\x04', volume])

            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        ChannelStates = {
            '1': b'\x0A',
            '2': b'\x14',
            '3': b'\x1E',
            '4': b'\x28'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            GainCmdString = b''.join([b'\x4C\x00\x00\x0C\x18\x03\x00\x78\x00', ChannelStates[channel_val], b'\x00\x00'])
            res = self.__UpdateHelper('Gain', GainCmdString, value, qualifier)
            if res:
                try:
                    volume = unpack('>l', res[12:16])[0]
                    value = float(volume / 10)
                    self.WriteStatus('Gain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGain')

    def SetImpedance(self, value, qualifier):

        FrequencyStates = ['High', 'Low']
        ValueTypeStates = ['Minimum', 'Maximum']
        NumberStates = ['1', '2', '3', '4']

        ValueConstraints = {
            'Min': 0,
            'Max': 10000
            }

        SubIDStates = {
            'High_Minimum_1': 110,
            'High_Maximum_1': 111,
            'Low_Minimum_1': 112,
            'Low_Maximum_1': 113,
            'High_Minimum_2': 120,
            'High_Maximum_2': 121,
            'Low_Minimum_2': 122,
            'Low_Maximum_2': 123,
            'High_Minimum_3': 130,
            'High_Maximum_3': 131,
            'Low_Minimum_3': 132,
            'Low_Maximum_3': 133,
            'High_Minimum_4': 140,
            'High_Maximum_4': 141,
            'Low_Minimum_4': 142,
            'Low_Maximum_4': 143
        }

        freq_val = qualifier['Frequency']
        type_val = qualifier['Value Type']
        numb_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and freq_val in FrequencyStates and type_val in ValueTypeStates and numb_val in NumberStates:
            sub_idval = '_'.join([freq_val, type_val, numb_val])
            ImpedanceCmdString = b''.join([b'\x4C\x00\x00\x10\x21\x03\x00\x3D', pack('>h', SubIDStates[sub_idval]), b'\x00\x04', pack('>f', value)])
            self.__SetHelper('Impedance', ImpedanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImpedance')

    def UpdateImpedance(self, value, qualifier):

        FrequencyStates = ['High', 'Low']
        ValueTypeStates = ['Minimum', 'Maximum']
        NumberStates = ['1', '2', '3', '4']

        SubIDStates = {               # SubIDValues = {
            'High_Minimum_1': 110,       # b'\x6E' : ['High', 'Minimum', '1'],
            'High_Maximum_1': 111,       # b'\x6F' : ['High', 'Maximum', '1'],
            'Low_Minimum_1': 112,       # b'\x70' : ['Low', 'Minimum', '1'],
            'Low_Maximum_1': 113,       # b'\x71' : ['Low', 'Maximum', '1'],
            'High_Minimum_2': 120,       # b'\x78' : ['High', 'Minimum', '2'],
            'High_Maximum_2': 121,       # b'\x79' : ['High', 'Maximum', '2'],
            'Low_Minimum_2': 122,       # b'\x7A' : ['Low', 'Minimum', '2'],
            'Low_Maximum_2': 123,       # b'\x7B' : ['Low', 'Maximum', '2'],
            'High_Minimum_3': 130,       # b'\x82' : ['High', 'Minimum', '3'],
            'High_Maximum_3': 131,       # b'\x83' : ['High', 'Maximum', '3'],
            'Low_Minimum_3': 132,       # b'\x84' : ['Low', 'Minimum', '3'],
            'Low_Maximum_3': 133,       # b'\x85' : ['Low', 'Maximum', '3'],
            'High_Minimum_4': 140,       # b'\x8C' : ['High', 'Minimum', '4'],
            'High_Maximum_4': 141,       # b'\x8D' : ['High', 'Maximum', '4'],
            'Low_Minimum_4': 142,       # b'\x8E' : ['Low', 'Minimum', '4'],
            'Low_Maximum_4': 143        # b'\x8F' : ['Low', 'Maximum', '4']
        }                             # }

        freq_val = qualifier['Frequency']
        type_val = qualifier['Value Type']
        numb_val = qualifier['Number']
        if freq_val in FrequencyStates and type_val in ValueTypeStates and numb_val in NumberStates:
            sub_idval = '_'.join([freq_val, type_val, numb_val])
            ImpedanceCmdString = b''.join([b'\x4C\x00\x00\x0C\x20\x03\x00\x3D', pack('>h', SubIDStates[sub_idval]), b'\x00\x00'])
            res = self.__UpdateHelper('Impedance', ImpedanceCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>f', res[12:16])[0]
                    if 0.0 <= value <= 10000.0:
                        self.WriteStatus('Impedance', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Impedance: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateImpedance')

    def SetInputAandB(self, value, qualifier):

        ValueStateValues = {
            'AES': b'\x01',
            'Analog': b'\x00'
        }

        InputAandBCmdString = b'\x4C\x00\x00\x10\x19\x03\x00\x02\x00\x1E\x00\x04\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('InputAandB', InputAandBCmdString, value, qualifier)

    def SetInputCandD(self, value, qualifier):

        ValueStateValues = {
            'AES': b'\x01',
            'Analog': b'\x00'
        }

        InputCandDCmdString = b'\x4C\x00\x00\x10\x19\x03\x00\x02\x00\x28\x00\x04\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('InputCandD', InputCandDCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ChannelStates = {
            '1': b'\x0A',
            '2': b'\x0B',
            '3': b'\x0C',
            '4': b'\x0D',
        }

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        channel = qualifier['Channel']

        if channel == 'All':
            header = b'\x4C\x00\x00\x34'
            ch1 = b'\x19\x03\x00\x64\x00\x0A\x00\x04\x00\x00\x00' + ValueStateValues[value]
            ch2 = b'\x19\x03\x00\x64\x00\x0B\x00\x04\x00\x00\x00' + ValueStateValues[value]
            ch3 = b'\x19\x03\x00\x64\x00\x0C\x00\x04\x00\x00\x00' + ValueStateValues[value]
            ch4 = b'\x19\x03\x00\x64\x00\x0D\x00\x04\x00\x00\x00' + ValueStateValues[value]
            MuteCmdString = b''.join([header, ch1, ch2, ch3, ch4])
        else:
            MuteCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x64\x00', ChannelStates[channel], b'\x00\x04\x00\x00\x00', ValueStateValues[value]])

        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPilotToneFrequency(self, value, qualifier):

        ValueConstraints = {
            'Min': 10,
            'Max': 22000
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PilotToneFrequencyCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D\x00\x64\x00\x04', pack('>l', value)])
            self.__SetHelper('PilotToneFrequency', PilotToneFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPilotToneFrequency')

    def UpdatePilotToneFrequency(self, value, qualifier):

        PilotToneFrequencyCmdString = b'\x4C\x00\x00\x0C\x18\x03\x00\x3D\x00\x64\x00\x00'
        res = self.__UpdateHelper('PilotToneFrequency', PilotToneFrequencyCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>l', res[12:16])[0]
                if 10 <= value <= 22000:
                    self.WriteStatus('PilotToneFrequency', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Pilot Tone Frequency: Invalid/unexpected response'])

    def SetPilotToneResolution(self, value, qualifier):

        ValueConstraints = {
            'Min': 10,
            'Max': 1000
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PilotToneResolutionCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D\x00\x66\x00\x04', pack('>l', value)])
            self.__SetHelper('PilotToneResolution', PilotToneResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPilotToneResolution')

    def UpdatePilotToneResolution(self, value, qualifier):

        PilotToneResolutionCmdString = b'\x4C\x00\x00\x0C\x18\x03\x00\x3D\x00\x66\x00\x00'
        res = self.__UpdateHelper('PilotToneResolution', PilotToneResolutionCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>l', res[12:16])[0]
                if 10 <= value <= 1000:
                    self.WriteStatus('PilotToneResolution', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Pilot Tone Resolution: Invalid/unexpected response'])

    def SetPilotToneThreshold(self, value, qualifier):

        ValueConstraints = {
            'Min': -1200,
            'Max': 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PilotToneThresholdCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D\x00\x65\x00\x04', pack('>l', value)])
            self.__SetHelper('PilotToneThreshold', PilotToneThresholdCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPilotToneThreshold')

    def UpdatePilotToneThreshold(self, value, qualifier):

        PilotToneThresholdCmdString = b'\x4C\x00\x00\x0C\x18\x03\x00\x3D\x00\x65\x00\x00'
        res = self.__UpdateHelper('PilotToneThreshold', PilotToneThresholdCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>l', res[12:16])[0]
                if -1200 <= value <= 0:
                    self.WriteStatus('PilotToneThreshold', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Pilot Tone Threshold: Invalid/unexpected response'])

    def SetPowerControl(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerControlCmdString = b'\x4C\x00\x00\x10\x19\x03\x00\x02\x00\x02\x00\x04\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('PowerControl', PowerControlCmdString, value, qualifier)

    def UpdatePowerControl(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerControlCmdString = b'\x4C\x00\x00\x0C\x18\x03\x00\x02\x00\x02\x00\x00'
        res = self.__UpdateHelper('PowerControl', PowerControlCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-1]]
                self.WriteStatus('PowerControl', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Control: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A'
        }

        if 1 <= int(value) <= 255:
            PresetRecallCmdString = b'\x4C\x00\x00\x10\x19\x03\x00\x5A\x00\x0A\x00\x04\x00\x00\x00' + pack('B', int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetSignalAmplitude(self, value, qualifier):

        FrequencyStates = {
            'High': 211,
            'Low': 221
        }

        ValueConstraints = {
            'Min': -1200,
            'Max': 0
            }

        freq_val = qualifier['Frequency']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and freq_val in FrequencyStates:
            SignalAmplitudeCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x04', pack('>l', value)])
            self.__SetHelper('SignalAmplitude', SignalAmplitudeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalAmplitude')

    def UpdateSignalAmplitude(self, value, qualifier):

        FrequencyStates = {
            'High': 211,  # b'\xD3'
            'Low': 221   # b'\xDD'
        }

        freq_val = qualifier['Frequency']
        if freq_val in FrequencyStates:
            SignalAmplitudeCmdString = b''.join([b'\x4C\x00\x00\x0C\x18\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x00'])
            res = self.__UpdateHelper('SignalAmplitude', SignalAmplitudeCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>l', res[12:16])[0]
                    if -1200 <= value <= 0:
                        self.WriteStatus('SignalAmplitude', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Signal Amplitude: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSignalAmplitude')

    def SetSignalFadeTime(self, value, qualifier):

        FrequencyStates = {
            'High': 213,
            'Low': 223
        }

        ValueConstraints = {
            'Min': 10,
            'Max': 1000
            }

        freq_val = qualifier['Frequency']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and freq_val in FrequencyStates:
            SignalFadeTimeCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x04', pack('>l', value)])
            self.__SetHelper('SignalFadeTime', SignalFadeTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalFadeTime')

    def UpdateSignalFadeTime(self, value, qualifier):

        FrequencyStates = {
            'High': 213,        # b'\xD5'
            'Low': 223         # b'\xDF'
        }

        freq_val = qualifier['Frequency']
        if freq_val in FrequencyStates:
            SignalFadeTimeCmdString = b''.join([b'\x4C\x00\x00\x0C\x18\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x00'])
            res = self.__UpdateHelper('SignalFadeTime', SignalFadeTimeCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>l', res[12:16])[0]
                    if 10 <= value <= 1000:
                        self.WriteStatus('SignalFadeTime', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Signal Fade Time: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSignalFadeTime')

    def SetSignalFrequency(self, value, qualifier):

        FrequencyStates = {
            'High': 210,
            'Low': 220
        }

        ValueConstraints = {
            'Min': 10,
            'Max': 22000
            }

        freq_val = qualifier['Frequency']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and freq_val in FrequencyStates:
            SignalFrequencyCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x04', pack('>l', value)])
            self.__SetHelper('SignalFrequency', SignalFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalFrequency')

    def UpdateSignalFrequency(self, value, qualifier):

        FrequencyStates = {
            'High': 210,  # b'\xD2'
            'Low': 220  # b'\xDC'
        }

        freq_val = qualifier['Frequency']
        if freq_val in FrequencyStates:
            SignalFrequencyCmdString = b''.join([b'\x4C\x00\x00\x0C\x18\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x00'])
            res = self.__UpdateHelper('SignalFrequency', SignalFrequencyCmdString, value, qualifier)
            if res:
                try:
                    value = value = unpack('>l', res[12:16])[0]
                    if 10 <= value <= 22000:
                        self.WriteStatus('SignalFrequency', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Signal Frequency: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSignalFrequency')

    def SetSignalGFTSize(self, value, qualifier):

        FrequencyStates = {
            'High': 214,
            'Low': 224
        }

        ValueConstraints = {
            'Min': 64,
            'Max': 32768
            }

        freq_val = qualifier['Frequency']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and freq_val in FrequencyStates:
            SignalGFTSizeCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x04', pack('>l', value)])
            self.__SetHelper('SignalGFTSize', SignalGFTSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalGFTSize')

    def UpdateSignalGFTSize(self, value, qualifier):

        FrequencyStates = {
            'High': 214,  # b'\xD6'
            'Low': 224  # b'\xE0'
        }
        freq_val = qualifier['Frequency']
        if freq_val in FrequencyStates:
            SignalGFTSizeCmdString = b''.join([b'\x4C\x00\x00\x0C\x18\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x00'])
            res = self.__UpdateHelper('SignalGFTSize', SignalGFTSizeCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>l', res[12:16])[0]
                    if 64 <= value <= 32768:
                        self.WriteStatus('SignalGFTSize', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Signal GFT Size: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSignalGFTSize')

    def SetSignalHoldTime(self, value, qualifier):

        FrequencyStates = {
            'High': 212,
            'Low': 222
        }

        ValueConstraints = {
            'Min': 100,
            'Max': 5000
            }

        freq_val = qualifier['Frequency']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and freq_val in FrequencyStates:
            SignalHoldTimeCmdString = b''.join([b'\x4C\x00\x00\x10\x19\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x04', pack('>l', value)])
            self.__SetHelper('SignalHoldTime', SignalHoldTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalHoldTime')

    def UpdateSignalHoldTime(self, value, qualifier):

        FrequencyStates = {
            'High': 212,       # b'\xD4'
            'Low': 222        # b'\xDE'
        }

        freq_val = qualifier['Frequency']
        if freq_val in FrequencyStates:
            SignalHoldTimeCmdString = b''.join([b'\x4C\x00\x00\x0C\x18\x03\x00\x3D', pack('>h', FrequencyStates[freq_val]), b'\x00\x00'])
            res = self.__UpdateHelper('SignalHoldTime', SignalHoldTimeCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>l', res[12:16])[0]
                    if 100 <= value <= 5000:
                        self.WriteStatus('SignalHoldTime', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Signal Hold Time: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSignalHoldTime')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorStates = {
            b'\x04': 'Read Error with No Data.',
            b'\x05': 'Write Error with No Data.',
            b'\x0C': 'Read Error with Character Data.',
            b'\x0D': 'Write Error with Character Data.',
            b'\x14': 'Read Error with Short Data.',
            b'\x15': 'Write Error with Short Data.',
            b'\x1C': 'Read Error with Integer Data.',
            b'\x1D': 'Write Error with Integer Data.',
            b'\x24': 'Read Error with Float Data.',
            b'\x25': 'Write Error with Float Data.',
        }

        if response and response[4:5] in ErrorStates:
            self.Error([ErrorStates[response[4:5]]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=12)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=16)
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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

