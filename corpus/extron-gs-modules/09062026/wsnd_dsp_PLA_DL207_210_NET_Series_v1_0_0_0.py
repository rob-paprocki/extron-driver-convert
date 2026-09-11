from extronlib.interface import SerialInterface, EthernetClientInterface
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
            'AmplifierStatus': {'Parameters': ['Loop'], 'Status': {}},
            'HeadphoneMute': {'Status': {}},
            'HeadphoneSource': {'Status': {}},
            'HeadphoneVolume': {'Status': {}},
            'Input10dBVGain': {'Parameters': ['Channel'], 'Status': {}},
            'Input4dBuGain': {'Parameters': ['Channel'], 'Status': {}},
            'InputCompressorAttackTime': {'Parameters': ['Channel'], 'Status': {}},
            'InputCompressorMakeUpVolume': {'Parameters': ['Channel'], 'Status': {}},
            'InputCompressorRatio': {'Parameters': ['Channel'], 'Status': {}},
            'InputCompressorReleaseTime': {'Parameters': ['Channel'], 'Status': {}},
            'InputCompressorThreshold': {'Parameters': ['Channel'], 'Status': {}},
            'InputEQBoostCutLevel': {'Parameters': ['Channel', 'EQ Band'], 'Status': {}},
            'InputEQFrequency': {'Parameters': ['Channel', 'EQ Band'], 'Status': {}},
            'InputHighPassFilterFrequency': {'Parameters': ['Channel'], 'Status': {}},
            'InputMicrophoneGain': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'InputPhantomPower': {'Parameters': ['Channel'], 'Status': {}},
            'InputType': {'Parameters': ['Channel'], 'Status': {}},
            'InputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'LoopMode': {'Status': {}},
            'OutputAGCAdjustment': {'Parameters': ['Channel'], 'Status': {}},
            'OutputAGCAttackTime': {'Parameters': ['Channel'], 'Status': {}},
            'OutputAGCHoldTime': {'Parameters': ['Channel'], 'Status': {}},
            'OutputAGCPresetType': {'Parameters': ['Channel'], 'Status': {}},
            'OutputAGCReleaseTime': {'Parameters': ['Channel'], 'Status': {}},
            'OutputCalibrationLevel': {'Parameters': ['Channel'], 'Status': {}},
            'OutputDelayTime': {'Parameters': ['Channel'], 'Status': {}},
            'OutputEQBoostCutLevel': {'Parameters': ['Channel', 'EQ Band'], 'Status': {}},
            'OutputEQFrequency': {'Parameters': ['Channel', 'EQ Band'], 'Status': {}},
            'OutputHighPassFilterFrequency': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLowPassFilterFrequency': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMCEQBoostLevel': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMCEQFrequency': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMixerVolume': {'Parameters': ['Channel', 'Input'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'RecallPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
        }

    def UpdateAmplifierStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Sleeping',
            '2': 'Amplifier is clipping',
            '3': 'Amplifier temperature is approaching shutdown point',
            '4': 'Amplifier is faulted',
            '5': 'Amplifier status is unknown'
        }

        LoopStates = {
            'A': '1',
            'B': '2'
        }

        AmplifierStatusCmdString = '=gamp{0}!'.format(LoopStates[qualifier['Loop']])
        res = self.__UpdateHelper('AmplifierStatus', AmplifierStatusCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[res.index(':') + 1:-1]]
                self.WriteStatus('AmplifierStatus', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAmplifierStatus')

    def SetHeadphoneMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        HeadphoneMuteCmdString = '=shpmute:{0}!'.format(ValueStateValues[value])
        self.__SetHelper('HeadphoneMute', HeadphoneMuteCmdString, value, qualifier)

    def UpdateHeadphoneMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        HeadphoneMuteCmdString = '=ghpmute!'
        res = self.__UpdateHelper('HeadphoneMute', HeadphoneMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[res.index(':') + 1:-1]]
                self.WriteStatus('HeadphoneMute', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateHeadphoneMute')

    def SetHeadphoneSource(self, value, qualifier):

        ValueStateValues = {
            'Loop A output': '0',
            'Loop B output': '1',
            'Digital L input': '2',
            'Digital R input': '3',
            'Input 1 input': '4',
            'Input 2 input': '5',
            'Line 1 input': '6',
            'Line 2 input': '7',
            '70-100V input': '8'
        }

        HeadphoneSourceCmdString = '=shpsel:{0}!'.format(ValueStateValues[value])
        self.__SetHelper('HeadphoneSource', HeadphoneSourceCmdString, value, qualifier)

    def UpdateHeadphoneSource(self, value, qualifier):

        ValueStateValues = {
            '0': 'Loop A output',
            '1': 'Loop B output',
            '2': 'Digital L input',
            '3': 'Digital R input',
            '4': 'Input 1 input',
            '5': 'Input 2 input',
            '6': 'Line 1 input',
            '7': 'Line 2 input',
            '8': '70-100V input'
        }

        HeadphoneSourceCmdString = '=ghpsel!'
        res = self.__UpdateHelper('HeadphoneSource', HeadphoneSourceCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[res.index(':') + 1:-1]]
                self.WriteStatus('HeadphoneSource', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateHeadphoneSource')

    def SetHeadphoneVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -96.0,
            'Max': 0.0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            HeadphoneVolumeCmdString = '=shpvol:{0}!'.format(int(value * 10))
            self.__SetHelper('HeadphoneVolume', HeadphoneVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetHeadphoneVolume')

    def UpdateHeadphoneVolume(self, value, qualifier):

        HeadphoneVolumeCmdString = '=ghpvol!'
        res = self.__UpdateHelper('HeadphoneVolume', HeadphoneVolumeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = float(int(res[res.index(':') + 1:-1]) / 10)
                self.WriteStatus('HeadphoneVolume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateHeadphoneVolume')

    def SetInput10dBVGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -12,
            'Max': 39
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 3 <= int(channel) <= 4:
            Input10dBVGainCmdString = '=s{0}@igain:{1}!'.format(channel, value)
            self.__SetHelper('Input10dBVGain', Input10dBVGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInput10dBVGain')

    def UpdateInput10dBVGain(self, value, qualifier):

        channel = qualifier['Channel']
        if 3 <= int(channel) <= 4:
            Input10dBVGainCmdString = '=g{0}@igain!'.format(1)
            res = self.__UpdateHelper('Input10dBVGain', Input10dBVGainCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1])
                    if -12 <= value <= 39:
                        self.WriteStatus('Input10dBVGain', value, qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateInput10dBVGain')
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInput10dBVGain')
        else:
            print('Invalid Command for UpdateInput10dBVGain')

    def SetInput4dBuGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -6,
            'Max': 6
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 3 <= int(channel) <= 4:
            Input4dBuGainCmdString = '=s{0}@igain:{1}!'.format(channel, value)
            self.__SetHelper('Input4dBuGain', Input4dBuGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInput4dBuGain')

    def UpdateInput4dBuGain(self, value, qualifier):

        channel = qualifier['Channel']
        if 3 <= int(channel) <= 4:
            Input4dBuGainCmdString = '=g{0}@igain!'.format(2)
            res = self.__UpdateHelper('Input4dBuGain', Input4dBuGainCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1])
                    if -6 <= value <= 6:
                        self.WriteStatus('Input4dBuGain', value, qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateInput4dBuGain')
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInput4dBuGain')
        else:
            print('Invalid Command for UpdateInput4dBuGain')

    def SetInputCompressorAttackTime(self, value, qualifier):

        ValueConstraints = {
            'Min': 2,
            'Max': 500
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 12:
            InputCompressorAttackTimeCmdString = '=s{0:01X}@icpatt1:{1}!'.format(channel, int(value / 2))
            self.__SetHelper('InputCompressorAttackTime', InputCompressorAttackTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputCompressorAttackTime')

    def UpdateInputCompressorAttackTime(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputCompressorAttackTimeCmdString = '=g{0:01X}@icpatt1!'.format(channel)
            res = self.__UpdateHelper('InputCompressorAttackTime', InputCompressorAttackTimeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1]) * 2
                    self.WriteStatus('InputCompressorAttackTime', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputCompressorAttackTime')
        else:
            print('Invalid Command for UpdateInputCompressorAttackTime')

    def SetInputCompressorMakeUpVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0.0,
            'Max': 40.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 12:
            InputCompressorMakeUpVolumeCmdString = '=s{0:01X}@icpmak1:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('InputCompressorMakeUpVolume', InputCompressorMakeUpVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputCompressorMakeUpVolume')

    def UpdateInputCompressorMakeUpVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputCompressorMakeUpVolumeCmdString = '=g{0:01X}@icpmak1!'.format(channel)
            res = self.__UpdateHelper('InputCompressorMakeUpVolume', InputCompressorMakeUpVolumeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('InputCompressorMakeUpVolume', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputCompressorMakeUpVolume')
        else:
            print('Invalid Command for UpdateInputCompressorMakeUpVolume')

    def SetInputCompressorRatio(self, value, qualifier):

        ValueConstraints = {
            'Min': 1.0,
            'Max': 10.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 12:
            InputCompressorRatioCmdString = '=s{0:01X}@icprat1:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('InputCompressorRatio', InputCompressorRatioCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputCompressorRatio')

    def UpdateInputCompressorRatio(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputCompressorRatioCmdString = '=g{0:01X}@icprat1!'.format(channel)
            res = self.__UpdateHelper('InputCompressorRatio', InputCompressorRatioCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('InputCompressorRatio', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputCompressorRatio')
        else:
            print('Invalid Command for UpdateInputCompressorRatio')

    def SetInputCompressorReleaseTime(self, value, qualifier):

        ValueConstraints = {
            'Min': 10,
            'Max': 2500
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 12:
            InputCompressorReleaseTimeCmdString = '=s{0:01X}@icprel1:{1}!'.format(channel, int(value / 10))
            self.__SetHelper('InputCompressorReleaseTime', InputCompressorReleaseTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputCompressorReleaseTime')

    def UpdateInputCompressorReleaseTime(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputCompressorReleaseTimeCmdString = '=g{0:01X}@icprel1!'.format(channel)
            res = self.__UpdateHelper('InputCompressorReleaseTime', InputCompressorReleaseTimeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1]) * 10
                    self.WriteStatus('InputCompressorReleaseTime', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputCompressorReleaseTime')
        else:
            print('Invalid Command for UpdateInputCompressorReleaseTime')

    def SetInputCompressorThreshold(self, value, qualifier):

        ValueConstraints = {
            'Min': -96.0,
            'Max': 0.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 12:
            InputCompressorThresholdCmdString = '=s{0:01X}@icpthr1:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('InputCompressorThreshold', InputCompressorThresholdCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputCompressorThreshold')

    def UpdateInputCompressorThreshold(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputCompressorThresholdCmdString = '=g{0:01X}@icpthr1!'.format(channel)
            res = self.__UpdateHelper('InputCompressorThreshold', InputCompressorThresholdCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('InputCompressorThreshold', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputCompressorThreshold')
        else:
            print('Invalid Command for UpdateInputCompressorThreshold')

    def SetInputEQBoostCutLevel(self, value, qualifier):

        EQBandStates = {
            'Bass': 'b',
            'Mid': '1',
            'Treble': 't'
        }

        ValueConstraints = {
            'Min': -12.0,
            'Max': 12.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 12:
            InputEQBoostCutLevelCmdString = '=s{0:01X}@ieq{1}:{2}!'.format(channel, EQBandStates[qualifier['EQ Band']], int(value * 10))
            self.__SetHelper('InputEQBoostCutLevel', InputEQBoostCutLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputEQBoostCutLevel')

    def UpdateInputEQBoostCutLevel(self, value, qualifier):

        EQBandStates = {
            'Bass': 'b',
            'Mid': '1',
            'Treble': 't'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputEQBoostCutLevelCmdString = '=g{0:01X}@ieq{1}!'.format(channel, EQBandStates[qualifier['EQ Band']])
            res = self.__UpdateHelper('InputEQBoostCutLevel', InputEQBoostCutLevelCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('InputEQBoostCutLevel', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputEQBoostCutLevel')
        else:
            print('Invalid Command for UpdateInputEQBoostCutLevel')

    def SetInputEQFrequency(self, value, qualifier):

        EQBandStates = {
            'Bass': 'fb',
            'Mid': 'f1',
            'Treble': 'ft'
        }

        ValueStateValues = {
            '20 Hz': '20',
            '25 Hz': '25',
            '32 Hz': '32',
            '40 Hz': '40',
            '50 Hz': '50',
            '63 Hz': '63',
            '80 Hz': '80',
            '100 Hz': '100',
            '125 Hz': '125',
            '160 Hz': '160',
            '200 Hz': '200',
            '250 Hz': '250',
            '315 Hz': '315',
            '400 Hz': '400',
            '500 Hz': '500',
            '630 Hz': '630',
            '800 Hz': '800',
            '1000 Hz': '1000',
            '1250 Hz': '1250',
            '1600 Hz': '1600',
            '2000 Hz': '2000',
            '2500 Hz': '2500',
            '3150 Hz': '3150',
            '4000 Hz': '4000',
            '5000 Hz': '5000',
            '6300 Hz': '6300',
            '8000 Hz': '8000',
            '10000 Hz': '10000',
            '12500 Hz': '12500',
            '16000 Hz': '16000',
            '20000 Hz': '20000'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputEQFrequencyCmdString = '=s{0:01X}@ieq{1}:{2}!'.format(channel, EQBandStates[qualifier['EQ Band']], ValueStateValues[value])
            self.__SetHelper('InputEQFrequency', InputEQFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputEQFrequency')

    def UpdateInputEQFrequency(self, value, qualifier):

        EQBandStates = {
            'Bass': 'fb',
            'Mid': 'f1',
            'Treble': 'ft'
        }

        ValueStateValues = {
            '20': '20 Hz',
            '25': '25 Hz',
            '32': '32 Hz',
            '40': '40 Hz',
            '50': '50 Hz',
            '63': '63 Hz',
            '80': '80 Hz',
            '100': '100 Hz',
            '125': '125 Hz',
            '160': '160 Hz',
            '200': '200 Hz',
            '250': '250 Hz',
            '315': '315 Hz',
            '400': '400 Hz',
            '500': '500 Hz',
            '630': '630 Hz',
            '800': '800 Hz',
            '1000': '1000 Hz',
            '1250': '1250 Hz',
            '1600': '1600 Hz',
            '2000': '2000 Hz',
            '2500': '2500 Hz',
            '3150': '3150 Hz',
            '4000': '4000 Hz',
            '5000': '5000 Hz',
            '6300': '6300 Hz',
            '8000': '8000 Hz',
            '10000': '10000 Hz',
            '12500': '12500 Hz',
            '16000': '16000 Hz',
            '20000': '20000 Hz'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputEQFrequencyCmdString = '=g{0:01X}@ieq{1}!'.format(channel, EQBandStates[qualifier['EQ Band']])
            res = self.__UpdateHelper('InputEQFrequency', InputEQFrequencyCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('InputEQFrequency', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputEQFrequency')
        else:
            print('Invalid Command for UpdateInputEQFrequency')

    def SetInputHighPassFilterFrequency(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            '31 Hz': '1',
            '62 Hz': '2',
            '125 Hz': '3',
            '500 Hz': '4'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputHighPassFilterFrequencyCmdString = '=s{0:01X}@ihpf:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('InputHighPassFilterFrequency', InputHighPassFilterFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputHighPassFilterFrequency')

    def UpdateInputHighPassFilterFrequency(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': '31 Hz',
            '2': '62 Hz',
            '3': '125 Hz',
            '4': '500 Hz'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputHighPassFilterFrequencyCmdString = '=g{0:01X}@ihpf!'.format(channel)
            res = self.__UpdateHelper('InputHighPassFilterFrequency', InputHighPassFilterFrequencyCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('InputHighPassFilterFrequency', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputHighPassFilterFrequency')
        else:
            print('Invalid Command for UpdateInputHighPassFilterFrequency')

    def SetInputMicrophoneGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 9,
            'Max': 60
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 3 <= int(channel) <= 4:
            InputMicrophoneGainCmdString = '=s{0}@igain:{1}!'.format(channel, value)
            self.__SetHelper('InputMicrophoneGain', InputMicrophoneGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputMicrophoneGain')

    def UpdateInputMicrophoneGain(self, value, qualifier):

        channel = qualifier['Channel']
        if 3 <= int(channel) <= 4:
            InputMicrophoneGainCmdString = '=g{0}@igain!'.format(channel)
            res = self.__UpdateHelper('InputMicrophoneGain', InputMicrophoneGainCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1])
                    if 9 <= value <= 60:
                        self.WriteStatus('InputMicrophoneGain', value, qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateInputMicrophoneGain')
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputMicrophoneGain')
        else:
            print('Invalid Command for UpdateInputMicrophoneGain')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputMuteCmdString = '=s{0:01X}@imute:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputMuteCmdString = '=g{0:01X}@imute!'.format(channel)
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('InputMute', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputMute')
        else:
            print('Invalid Command for UpdateInputMute')

    def SetInputPhantomPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = qualifier['Channel']
        if 3 <= int(channel) <= 4:
            InputPhantomPowerCmdString = '=s{0}@iphantom:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('InputPhantomPower', InputPhantomPowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputPhantomPower')

    def UpdateInputPhantomPower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = qualifier['Channel']
        if 3 <= int(channel) <= 4:
            InputPhantomPowerCmdString = '=g{0}@iphantom!'.format(channel)
            res = self.__UpdateHelper('InputPhantomPower', InputPhantomPowerCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('InputPhantomPower', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputPhantomPower')
        else:
            print('Invalid Command for UpdateInputPhantomPower')

    def SetInputType(self, value, qualifier):

        ValueStateValues = {
            'Microphone Level': '0',
            '+4 dBu Line Level': '1',
            '+8 dBu Line Level': '2',
            '-10 dBV Line Level': '3'
        }

        channel = qualifier['Channel']
        if 3 <= int(channel) <= 4:
            InputTypeCmdString = '=s{0}@itype:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('InputType', InputTypeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputType')

    def UpdateInputType(self, value, qualifier):

        ValueStateValues = {
            '0': 'Microphone Level',
            '1': '+4 dBu Line Level',
            '2': '+8 dBu Line Level',
            '3': '-10 dBV Line Level'
        }

        channel = qualifier['Channel']
        if 3 <= int(channel) <= 4:
            InputTypeCmdString = '=g{0}@itype!'.format(channel)
            res = self.__UpdateHelper('InputType', InputTypeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('InputType', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputType')
        else:
            print('Invalid Command for UpdateInputType')

    def SetInputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -96.0,
            'Max': 0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 12:
            InputVolumeCmdString = '=s{0:01X}@ivol:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputVolume')

    def UpdateInputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 12:
            InputVolumeCmdString = '=g{0:01X}@ivol!'.format(channel)
            res = self.__UpdateHelper('InputVolume', InputVolumeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('InputVolume', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputVolume')
        else:
            print('Invalid Command for UpdateInputVolume')

    def SetLoopMode(self, value, qualifier):

        ValueStateValues = {
            'Dual Loop': '1',
            'Phased Array': '2',
            'Speaker Out A': '3'
        }

        LoopModeCmdString = '=sloopmode:{0}!'.format(ValueStateValues[value])
        self.__SetHelper('LoopMode', LoopModeCmdString, value, qualifier)

    def UpdateLoopMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Dual Loop',
            '2': 'Phased Array',
            '3': 'Speaker Out A'
        }

        LoopModeCmdString = '=gloopmode!'
        res = self.__UpdateHelper('LoopMode', LoopModeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[res.index(':') + 1:-1]]
                self.WriteStatus('LoopMode', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLoopMode')

    def SetOutputAGCAdjustment(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10 and 0 <= int(value) <= 10:
            OutputAGCAdjustmentCmdString = '=s{0:01X}@oagcamt:{1}!'.format(channel, value)
            self.__SetHelper('OutputAGCAdjustment', OutputAGCAdjustmentCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputAGCAdjustment')

    def UpdateOutputAGCAdjustment(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputAGCAdjustmentCmdString = '=g{0:01X}@oagcamt!'.format(channel)
            res = self.__UpdateHelper('OutputAGCAdjustment', OutputAGCAdjustmentCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = res[res.index(':') + 1:-1]
                    self.WriteStatus('OutputAGCAdjustment', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputAGCAdjustment')
        else:
            print('Invalid Command for UpdateOutputAGCAdjustment')

    def SetOutputAGCAttackTime(self, value, qualifier):

        ValueConstraints = {
            'Min': 0.1,
            'Max': 1.5
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputAGCAttackTimeCmdString = '=s{0:01X}@oagcatt:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('OutputAGCAttackTime', OutputAGCAttackTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputAGCAttackTime')

    def UpdateOutputAGCAttackTime(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputAGCAttackTimeCmdString = '=g{0:01X}@oagcatt!'.format(channel)
            res = self.__UpdateHelper('OutputAGCAttackTime', OutputAGCAttackTimeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('OutputAGCAttackTime', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputAGCAttackTime')
        else:
            print('Invalid Command for UpdateOutputAGCAttackTime')

    def SetOutputAGCHoldTime(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 180
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputAGCHoldTimeCmdString = '=s{0:01X}@oagchld:{1}!'.format(channel, value)
            self.__SetHelper('OutputAGCHoldTime', OutputAGCHoldTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputAGCHoldTime')

    def UpdateOutputAGCHoldTime(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputAGCHoldTimeCmdString = '=g{0:01X}@oagchld!'.format(channel)
            res = self.__UpdateHelper('OutputAGCHoldTime', OutputAGCHoldTimeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1])
                    self.WriteStatus('OutputAGCHoldTime', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputAGCHoldTime')
        else:
            print('Invalid Command for UpdateOutputAGCHoldTime')

    def SetOutputAGCPresetType(self, value, qualifier):

        ValueStateValues = {
            'Custom': '0',
            'Music': '1',
            'Voice': '2'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputAGCPresetTypeCmdString = '=s{0:01X}@oagcpreset:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('OutputAGCPresetType', OutputAGCPresetTypeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputAGCPresetType')

    def UpdateOutputAGCPresetType(self, value, qualifier):

        ValueStateValues = {
            '0': 'Custom',
            '1': 'Music',
            '2': 'Voice'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputAGCPresetTypeCmdString = '=g{0:01X}@oagcpreset!'.format(channel)
            res = self.__UpdateHelper('OutputAGCPresetType', OutputAGCPresetTypeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('OutputAGCPresetType', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputAGCPresetType')
        else:
            print('Invalid Command for UpdateOutputAGCPresetType')

    def SetOutputAGCReleaseTime(self, value, qualifier):

        ValueConstraints = {
            'Min': 0.5,
            'Max': 3.5
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputAGCReleaseTimeCmdString = '=s{0:01X}@oagcrel:{1}!'.format(channel, int(value * 2))
            self.__SetHelper('OutputAGCReleaseTime', OutputAGCReleaseTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputAGCReleaseTime')

    def UpdateOutputAGCReleaseTime(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputAGCReleaseTimeCmdString = '=g{0:01X}@oagcrel!'.format(channel)
            res = self.__UpdateHelper('OutputAGCReleaseTime', OutputAGCReleaseTimeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 2)
                    self.WriteStatus('OutputAGCReleaseTime', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputAGCReleaseTime')
        else:
            print('Invalid Command for UpdateOutputAGCReleaseTime')

    def SetOutputCalibrationLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -96.0,
            'Max': 0.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputCalibrationLevelCmdString = '=s{0:01X}@ocal:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('OutputCalibrationLevel', OutputCalibrationLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputCalibrationLevel')

    def UpdateOutputCalibrationLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputCalibrationLevelCmdString = '=g{0:01X}@ocal!'.format(channel)
            res = self.__UpdateHelper('OutputCalibrationLevel', OutputCalibrationLevelCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('OutputCalibrationLevel', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputCalibrationLevel')
        else:
            print('Invalid Command for UpdateOutputCalibrationLevel')

    def SetOutputDelayTime(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 165
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 8:
            OutputDelayTimeCmdString = '=s{0}@odly:{1}!'.format(channel, value)
            self.__SetHelper('OutputDelayTime', OutputDelayTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputDelayTime')

    def UpdateOutputDelayTime(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 8:
            OutputDelayTimeCmdString = '=g{0}@odly!'.format(channel)
            res = self.__UpdateHelper('OutputDelayTime', OutputDelayTimeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1])
                    self.WriteStatus('OutputDelayTime', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputDelayTime')
        else:
            print('Invalid Command for UpdateOutputDelayTime')

    def SetOutputEQBoostCutLevel(self, value, qualifier):

        EQBandStates = {
            'Bass': 'b',
            'Mid': '1',
            'Treble': 't'
        }

        ValueConstraints = {
            'Min': -12.0,
            'Max': 12.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputEQBoostCutLevelCmdString = '=s{0:01X}@oeq{1}:{2}!'.format(channel, EQBandStates[qualifier['EQ Band']], int(value * 10))
            self.__SetHelper('OutputEQBoostCutLevel', OutputEQBoostCutLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputEQBoostCutLevel')

    def UpdateOutputEQBoostCutLevel(self, value, qualifier):

        EQBandStates = {
            'Bass': 'b',
            'Mid': '1',
            'Treble': 't'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputEQBoostCutLevelCmdString = '=g{0:01X}@oeq{1}!'.format(channel, EQBandStates[qualifier['EQ Band']])
            res = self.__UpdateHelper('OutputEQBoostCutLevel', OutputEQBoostCutLevelCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('OutputEQBoostCutLevel', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputEQBoostCutLevel')
        else:
            print('Invalid Command for UpdateOutputEQBoostCutLevel')

    def SetOutputEQFrequency(self, value, qualifier):

        EQBandStates = {
            'Bass': 'fb',
            'Mid': 'f1',
            'Treble': 'ft'
        }

        ValueStateValues = {
            '20 Hz': '20',
            '25 Hz': '25',
            '32 Hz': '32',
            '40 Hz': '40',
            '50 Hz': '50',
            '63 Hz': '63',
            '80 Hz': '80',
            '100 Hz': '100',
            '125 Hz': '125',
            '160 Hz': '160',
            '200 Hz': '200',
            '250 Hz': '250',
            '315 Hz': '315',
            '400 Hz': '400',
            '500 Hz': '500',
            '630 Hz': '630',
            '800 Hz': '800',
            '1000 Hz': '1000',
            '1250 Hz': '1250',
            '1600 Hz': '1600',
            '2000 Hz': '2000',
            '2500 Hz': '2500',
            '3150 Hz': '3150',
            '4000 Hz': '4000',
            '5000 Hz': '5000',
            '6300 Hz': '6300',
            '8000 Hz': '8000',
            '10000 Hz': '10000',
            '12500 Hz': '12500',
            '16000 Hz': '16000',
            '20000 Hz': '20000'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputEQFrequencyCmdString = '=s{0:01X}@oeq{1}:{2}!'.format(channel, EQBandStates[qualifier['EQ Band']], ValueStateValues[value])
            self.__SetHelper('OutputEQFrequency', OutputEQFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputEQFrequency')

    def UpdateOutputEQFrequency(self, value, qualifier):

        ValueStateValues = {
            '20': '20 Hz',
            '25': '25 Hz',
            '32': '32 Hz',
            '40': '40 Hz',
            '50': '50 Hz',
            '63': '63 Hz',
            '80': '80 Hz',
            '100': '100 Hz',
            '125': '125 Hz',
            '160': '160 Hz',
            '200': '200 Hz',
            '250': '250 Hz',
            '315': '315 Hz',
            '400': '400 Hz',
            '500': '500 Hz',
            '630': '630 Hz',
            '800': '800 Hz',
            '1000': '1000 Hz',
            '1250': '1250 Hz',
            '1600': '1600 Hz',
            '2000': '2000 Hz',
            '2500': '2500 Hz',
            '3150': '3150 Hz',
            '4000': '4000 Hz',
            '5000': '5000 Hz',
            '6300': '6300 Hz',
            '8000': '8000 Hz',
            '10000': '10000 Hz',
            '12500': '12500 Hz',
            '16000': '16000 Hz',
            '20000': '20000 Hz'
        }

        EQBandStates = {
            'Bass': 'fb',
            'Mid': 'f1',
            'Treble': 'ft'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputEQFrequencyCmdString = '=g{0:01X}@oeq{1}!'.format(channel, EQBandStates[qualifier['EQ Band']])
            res = self.__UpdateHelper('OutputEQFrequency', OutputEQFrequencyCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('OutputEQFrequency', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputEQFrequency')
        else:
            print('Invalid Command for UpdateOutputEQFrequency')

    def SetOutputHighPassFilterFrequency(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            '31 Hz': '1',
            '62 Hz': '2',
            '125 Hz': '3',
            '500 Hz': '4'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputHighPassFilterFrequencyCmdString = '=s{0:01X}@ohpf:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('OutputHighPassFilterFrequency', OutputHighPassFilterFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputHighPassFilterFrequency')

    def UpdateOutputHighPassFilterFrequency(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': '31 Hz',
            '2': '62 Hz',
            '3': '125 Hz',
            '4': '500 Hz'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputHighPassFilterFrequencyCmdString = '=g{0:01X}@ohpf!'.format(channel)
            res = self.__UpdateHelper('OutputHighPassFilterFrequency', OutputHighPassFilterFrequencyCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('OutputHighPassFilterFrequency', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputHighPassFilterFrequency')
        else:
            print('Invalid Command for UpdateOutputHighPassFilterFrequency')

    def SetOutputLowPassFilterFrequency(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            '16 kHz': '1',
            '8 kHz': '2',
            '6.3 kHz': '3'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputLowPassFilterFrequencyCmdString = '=s{0:01X}@olpf:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('OutputLowPassFilterFrequency', OutputLowPassFilterFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputLowPassFilterFrequency')

    def UpdateOutputLowPassFilterFrequency(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': '16 kHz',
            '2': '8 kHz',
            '3': '6.3 kHz'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputLowPassFilterFrequencyCmdString = '=g{0:01X}@olpf!'.format(channel)
            res = self.__UpdateHelper('OutputLowPassFilterFrequency', OutputLowPassFilterFrequencyCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('OutputLowPassFilterFrequency', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputLowPassFilterFrequency')
        else:
            print('Invalid Command for UpdateOutputLowPassFilterFrequency')

    def SetOutputMCEQBoostLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0.0,
            'Max': 12.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputMCEQBoostLevelCmdString = '=s{0:01X}@oeqmc:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('OutputMCEQBoostLevel', OutputMCEQBoostLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMCEQBoostLevel')

    def UpdateOutputMCEQBoostLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputMCEQBoostLevelCmdString = '=g{0:01X}@oeqmc!'.format(channel)
            res = self.__UpdateHelper('OutputMCEQBoostLevel', OutputMCEQBoostLevelCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('OutputMCEQBoostLevel', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputMCEQBoostLevel')
        else:
            print('Invalid Command for UpdateOutputMCEQBoostLevel')

    def SetOutputMCEQFrequency(self, value, qualifier):

        ValueConstraints = {
            'Min': 500,
            'Max': 9000
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputMCEQFrequencyCmdString = '=s{0:01X}@oeqfmc:{1}!'.format(channel, value)
            self.__SetHelper('OutputMCEQFrequency', OutputMCEQFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMCEQFrequency')

    def UpdateOutputMCEQFrequency(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputMCEQFrequencyCmdString = '=g{0:01X}@oeqfmc!'.format(channel)
            res = self.__UpdateHelper('OutputMCEQFrequency', OutputMCEQFrequencyCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = int(res[res.index(':') + 1:-1])
                    self.WriteStatus('OutputMCEQFrequency', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputMCEQFrequency')
        else:
            print('Invalid Command for UpdateOutputMCEQFrequency')

    def SetOutputMixerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -96.0,
            'Max': 0.0
        }

        channel = int(qualifier['Channel'])
        inputVal = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10 and 1 <= inputVal <= 7:
            OutputMixerVolumeCmdString = '=s{0:01X}@oivol{1}:{2}!'.format(channel, inputVal, int(value * 10))
            self.__SetHelper('OutputMixerVolume', OutputMixerVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMixerVolume')

    def UpdateOutputMixerVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        inputVal = int(qualifier['Input'])
        if 1 <= channel <= 10 and 1 <= inputVal <= 7:
            OutputMixerVolumeCmdString = '=g{0:01X}@oivol{1}!'.format(channel, inputVal)
            res = self.__UpdateHelper('OutputMixerVolume', OutputMixerVolumeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('OutputMixerVolume', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputMixerVolume')
        else:
            print('Invalid Command for UpdateOutputMixerVolume')

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputMuteCmdString = '=s{0:01X}@omute:{1}!'.format(channel, ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputMuteCmdString = '=g{0:01X}@omute!'.format(channel)
            res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = ValueStateValues[res[res.index(':') + 1:-1]]
                    self.WriteStatus('OutputMute', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputMute')
        else:
            print('Invalid Command for UpdateOutputMute')

    def SetOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -96.0,
            'Max': 0.0
        }

        channel = int(qualifier['Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= channel <= 10:
            OutputVolumeCmdString = '=s{0:01X}@ovol:{1}!'.format(channel, int(value * 10))
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 10:
            OutputVolumeCmdString = '=g{0:01X}@ovol!'.format(channel)
            res = self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    value = float(int(res[res.index(':') + 1:-1]) / 10)
                    self.WriteStatus('OutputVolume', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputVolume')
        else:
            print('Invalid Command for UpdateOutputVolume')

    def SetRecallPreset(self, value, qualifier):

        ValueStateValues = {
            'User 1': '1',
            'User 2': '2',
            'User 3': '3',
            'User 4': '4',
            'Factory 1': '11',
            'Factory 2': '12',
            'Factory 3': '13'
        }

        RecallPresetCmdString = '=slprs:{0}!'.format(ValueStateValues[value])
        self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)

    def SetSavePreset(self, value, qualifier):

        ValueStateValues = {
            'User 1': '1',
            'User 2': '2',
            'User 3': '3',
            'User 4': '4'
        }

        SavePresetCmdString = '=ssprs:{0}!'.format(ValueStateValues[value])
        self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='!')
            if not res:
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='!')
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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
