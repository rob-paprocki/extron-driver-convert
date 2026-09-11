from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
            'AnalogInputGainSwitch': {'Parameters': ['Channel'], 'Status': {}},
            'AnalogOutputGainSwitch': {'Parameters': ['Channel'], 'Status': {}},
            'AudioGain': {'Parameters': ['Channel'], 'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'AutomixerGateStatus': {'Parameters': ['Channel'], 'Status': {}},
            'AutomixerMode': {'Parameters': ['Channel'], 'Status': {}},
            'AutomixerOffAttenuation': {'Parameters': ['Channel'], 'Status': {}},
            'AutomixerPostGateMute': {'Parameters': ['Channel'], 'Status': {}},
            'CallStatus': { 'Status': {}},
            'CallStatusMode': { 'Status': {}},
            'DeviceAudioMute': {'Status': {}},
            'FlashLights': {'Status': {}},
            'MatrixMixerGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixMixerRouting': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'Preset': {'Status': {}},
            'Reboot': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP (0?0|1[12]) AUDIO_IN_LVL_SWITCH (LINE|AUX)_LVL >'), self.__MatchAnalogInputGainSwitch, None)
            self.AddMatchString(re.compile(b'< REP (0?0|1[78]) AUDIO_OUT_LVL_SWITCH (LINE|AUX|MIC)_LVL >'), self.__MatchAnalogOutputGainSwitch, None)
            self.AddMatchString(re.compile(b'< REP (0?[0-9]|1[0-9]|2[02-8]) AUDIO_GAIN_HI_RES (\d{4}) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP (0?[0-9]|1[0-9]|2[03-8]) AUDIO_MUTE (ON|OFF) >'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'< REP (0?[1-8]|22) AUTOMXR_GATE (ON|OFF) >'), self.__MatchAutomixerGateStatus, None)
            self.AddMatchString(re.compile(b'< REP (0?0|21) AUTOMXR_MODE (MANUAL|GAINSHARE|GATING) >'), self.__MatchAutomixerMode, None)
            self.AddMatchString(re.compile(b'< REP (0?0|21) AUTOMXR_OFF_ATT (\d{3}) >'), self.__MatchAutomixerOffAttenuation, None)
            self.AddMatchString(re.compile(b'< REP (0?0|21) AUTOMXR_MUTE (ON|OFF) >'), self.__MatchAutomixerPostGateMute, None)
            self.AddMatchString(re.compile(b'< REP ONHOOK_STATE (ON|OFF)HOOK >'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'< REP ONHOOK_ENABLE (ON|OFF) >'), self.__MatchCallStatusMode, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_AUDIO_MUTE (ON|OFF) >'), self.__MatchDeviceAudioMute, None)
            self.AddMatchString(re.compile(b'< REP FLASH (ON|OFF) >'), self.__MatchFlashLights, None)
            self.AddMatchString(re.compile(b'< REP (0?[1-9]|1[0-4]|21) MATRIX_MXR_GAIN (1[5-9]|2[03-8]) (\d{4}) >'), self.__MatchMatrixMixerGain, None)
            self.AddMatchString(re.compile(b'< REP (0?[1-9]|1[0-4]|21) MATRIX_MXR_ROUTE (1[5-9]|2[03-8]) (ON|OFF) >'), self.__MatchMatrixMixerRouting, None)
            self.AddMatchString(re.compile(b'< REP PRESET (0[1-9]|10) >'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)

    def SetAnalogInputGainSwitch(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Analog Input 1': '11',
            'Analog Input 2': '12'
        }

        ValueStateValues = {
            'Line Level': 'LINE',
            'AUX Level': 'AUX'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            AnalogInputGainSwitchCmdString = '< SET {0} AUDIO_IN_LVL_SWITCH {1}_LVL >'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('AnalogInputGainSwitch', AnalogInputGainSwitchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputGainSwitch')

    def UpdateAnalogInputGainSwitch(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Analog Input 1': '11',
            'Analog Input 2': '12'
        }

        if qualifier['Channel'] in ChannelStates:
            AnalogInputGainSwitchCmdString = '< GET {} AUDIO_IN_LVL_SWITCH >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AnalogInputGainSwitch', AnalogInputGainSwitchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogInputGainSwitch')

    def __MatchAnalogInputGainSwitch(self, match, tag):

        ChannelStates = {
            0: 'All Channels',
            11: 'Analog Input 1',
            12: 'Analog Input 2'
        }

        ValueStateValues = {
            'LINE': 'Line Level',
            'AUX': 'AUX Level'
        }

        qualifier = {'Channel': ChannelStates[int(match.group(1).decode())]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AnalogInputGainSwitch', value, qualifier)

    def SetAnalogOutputGainSwitch(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Analog Output 1': '17',
            'Analog Output 2': '18'
        }

        ValueStateValues = {
            'Line Level': 'LINE',
            'AUX Level': 'AUX',
            'Mic Level': 'MIC'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            AnalogOutputGainSwitchCmdString = '< SET {0} AUDIO_OUT_LVL_SWITCH {1}_LVL >'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('AnalogOutputGainSwitch', AnalogOutputGainSwitchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogOutputGainSwitch')

    def UpdateAnalogOutputGainSwitch(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Analog Output 1': '17',
            'Analog Output 2': '18'
        }

        if qualifier['Channel'] in ChannelStates:
            AnalogOutputGainSwitchCmdString = '< GET {} AUDIO_OUT_LVL_SWITCH >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AnalogOutputGainSwitch', AnalogOutputGainSwitchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogOutputGainSwitch')

    def __MatchAnalogOutputGainSwitch(self, match, tag):

        ChannelStates = {
            0: 'All Channels',
            17: 'Analog Output 1',
            18: 'Analog Output 2'
        }

        ValueStateValues = {
            'LINE': 'Line Level',
            'AUX': 'AUX Level',
            'MIC': 'Mic Level'
        }

        qualifier = {'Channel': ChannelStates[int(match.group(1).decode())]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AnalogOutputGainSwitch', value, qualifier)

    def SetAudioGain(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Dante Input 1 w/ Mic Processing': '01',
            'Dante Input 2 w/ Mic Processing': '02',
            'Dante Input 3 w/ Mic Processing': '03',
            'Dante Input 4 w/ Mic Processing': '04',
            'Dante Input 5 w/ Mic Processing': '05',
            'Dante Input 6 w/ Mic Processing': '06',
            'Dante Input 7 w/ Mic Processing': '07',
            'Dante Input 8 w/ Mic Processing': '08',
            'Dante Input 9': '09',
            'Dante Input 10': '10',
            'Analog Input 1': '11',
            'Analog Input 2': '12',
            'USB Input': '13',
            'Mobile Input': '14',
            'Dante Output 1': '15',
            'Dante Output 2': '16',
            'Analog Output 1': '17',
            'Analog Output 2': '18',
            'USB Output': '19',
            'Mobile Output': '20',
            'AEC Reference/Gate Inhibit Reference': '22',
            'Dante Output 3': '23',
            'Dante Output 4': '24',
            'Dante Output 5': '25',
            'Dante Output 6': '26',
            'Dante Output 7': '27',
            'Dante Output 8': '28'
        }

        if qualifier['Channel'] in ChannelStates and -110 <= value <= 30:
            AudioGainCmdString = '< SET {} AUDIO_GAIN_HI_RES {:04d} >'.format(ChannelStates[qualifier['Channel']], int((value + 110) * 10))
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Dante Input 1 w/ Mic Processing': '01',
            'Dante Input 2 w/ Mic Processing': '02',
            'Dante Input 3 w/ Mic Processing': '03',
            'Dante Input 4 w/ Mic Processing': '04',
            'Dante Input 5 w/ Mic Processing': '05',
            'Dante Input 6 w/ Mic Processing': '06',
            'Dante Input 7 w/ Mic Processing': '07',
            'Dante Input 8 w/ Mic Processing': '08',
            'Dante Input 9': '09',
            'Dante Input 10': '10',
            'Analog Input 1': '11',
            'Analog Input 2': '12',
            'USB Input': '13',
            'Mobile Input': '14',
            'Dante Output 1': '15',
            'Dante Output 2': '16',
            'Analog Output 1': '17',
            'Analog Output 2': '18',
            'USB Output': '19',
            'Mobile Output': '20',
            'AEC Reference/Gate Inhibit Reference': '22',
            'Dante Output 3': '23',
            'Dante Output 4': '24',
            'Dante Output 5': '25',
            'Dante Output 6': '26',
            'Dante Output 7': '27',
            'Dante Output 8': '28'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioGainCmdString = '< GET {} AUDIO_GAIN_HI_RES >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        ChannelStates = {
            0: 'All Channels',
            1: 'Dante Input 1 w/ Mic Processing',
            2: 'Dante Input 2 w/ Mic Processing',
            3: 'Dante Input 3 w/ Mic Processing',
            4: 'Dante Input 4 w/ Mic Processing',
            5: 'Dante Input 5 w/ Mic Processing',
            6: 'Dante Input 6 w/ Mic Processing',
            7: 'Dante Input 7 w/ Mic Processing',
            8: 'Dante Input 8 w/ Mic Processing',
            9: 'Dante Input 9',
            10: 'Dante Input 10',
            11: 'Analog Input 1',
            12: 'Analog Input 2',
            13: 'USB Input',
            14: 'Mobile Input',
            15: 'Dante Output 1',
            16: 'Dante Output 2',
            17: 'Analog Output 1',
            18: 'Analog Output 2',
            19: 'USB Output',
            20: 'Mobile Output',
            22: 'AEC Reference/Gate Inhibit Reference',
            23: 'Dante Output 3',
            24: 'Dante Output 4',
            25: 'Dante Output 5',
            26: 'Dante Output 6',
            27: 'Dante Output 7',
            28: 'Dante Output 8',
        }

        qualifier = {'Channel': ChannelStates[int(match.group(1).decode())]}
        value = (int(match.group(2).decode()) / 10) - 110.0
        if -110 <= value <= 30:
            self.WriteStatus('AudioGain', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Dante Input 1 w/ Mic Processing': '01',
            'Dante Input 2 w/ Mic Processing': '02',
            'Dante Input 3 w/ Mic Processing': '03',
            'Dante Input 4 w/ Mic Processing': '04',
            'Dante Input 5 w/ Mic Processing': '05',
            'Dante Input 6 w/ Mic Processing': '06',
            'Dante Input 7 w/ Mic Processing': '07',
            'Dante Input 8 w/ Mic Processing': '08',
            'Dante Input 9': '09',
            'Dante Input 10': '10',
            'Analog Input 1': '11',
            'Analog Input 2': '12',
            'USB Input': '13',
            'Mobile Input': '14',
            'Dante Output 1': '15',
            'Dante Output 2': '16',
            'Analog Output 1': '17',
            'Analog Output 2': '18',
            'USB Output': '19',
            'Mobile Output': '20',
            'Dante Output 3': '23',
            'Dante Output 4': '24',
            'Dante Output 5': '25',
            'Dante Output 6': '26',
            'Dante Output 7': '27',
            'Dante Output 8': '28'
        }

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            AudioMuteCmdString = '< SET {0} AUDIO_MUTE {1} >'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Dante Input 1 w/ Mic Processing': '01',
            'Dante Input 2 w/ Mic Processing': '02',
            'Dante Input 3 w/ Mic Processing': '03',
            'Dante Input 4 w/ Mic Processing': '04',
            'Dante Input 5 w/ Mic Processing': '05',
            'Dante Input 6 w/ Mic Processing': '06',
            'Dante Input 7 w/ Mic Processing': '07',
            'Dante Input 8 w/ Mic Processing': '08',
            'Dante Input 9': '09',
            'Dante Input 10': '10',
            'Analog Input 1': '11',
            'Analog Input 2': '12',
            'USB Input': '13',
            'Mobile Input': '14',
            'Dante Output 1': '15',
            'Dante Output 2': '16',
            'Analog Output 1': '17',
            'Analog Output 2': '18',
            'USB Output': '19',
            'Mobile Output': '20',
            'Dante Output 3': '23',
            'Dante Output 4': '24',
            'Dante Output 5': '25',
            'Dante Output 6': '26',
            'Dante Output 7': '27',
            'Dante Output 8': '28'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioMuteCmdString = '< GET {} AUDIO_MUTE >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ChannelStates = {
            0: 'All Channels',
            1: 'Dante Input 1 w/ Mic Processing',
            2: 'Dante Input 2 w/ Mic Processing',
            3: 'Dante Input 3 w/ Mic Processing',
            4: 'Dante Input 4 w/ Mic Processing',
            5: 'Dante Input 5 w/ Mic Processing',
            6: 'Dante Input 6 w/ Mic Processing',
            7: 'Dante Input 7 w/ Mic Processing',
            8: 'Dante Input 8 w/ Mic Processing',
            9: 'Dante Input 9',
            10: 'Dante Input 10',
            11: 'Analog Input 1',
            12: 'Analog Input 2',
            13: 'USB Input',
            14: 'Mobile Input',
            15: 'Dante Output 1',
            16: 'Dante Output 2',
            17: 'Analog Output 1',
            18: 'Analog Output 2',
            19: 'USB Output',
            20: 'Mobile Output',
            23: 'Dante Output 3',
            24: 'Dante Output 4',
            25: 'Dante Output 5',
            26: 'Dante Output 6',
            27: 'Dante Output 7',
            28: 'Dante Output 8',
        }

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[int(match.group(1).decode())]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def UpdateAutomixerGateStatus(self, value, qualifier):

        ChannelStates = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            'Gate Inhibit': '22'
        }
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            AutomixerGateStatusCmdString = '< GET {} AUTOMXR_GATE >'.format(ChannelStates[channel_val])
            self.__UpdateHelper('AutomixerGateStatus', AutomixerGateStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerGateStatus')

    def __MatchAutomixerGateStatus(self, match, tag):

        ChannelStates = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            22: 'Gate Inhibit'
        }

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[int(match.group(1).decode())]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerGateStatus', value, qualifier)

    def SetAutomixerMode(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Automixer Output': '21'
        }

        ValueStateValues = {
            'Manual': 'MANUAL',
            'Gain Share': 'GAINSHARE',
            'Gating': 'GATING'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            AutomixerModeCmdString = '< SET {0} AUTOMXR_MODE {1} >'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('AutomixerMode', AutomixerModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomixerMode')

    def UpdateAutomixerMode(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Automixer Output': '21'
        }

        if qualifier['Channel'] in ChannelStates:
            AutomixerModeCmdString = '< GET {} AUTOMXR_MODE >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AutomixerMode', AutomixerModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerMode')

    def __MatchAutomixerMode(self, match, tag):

        ChannelStates = {
            0: 'All Channels',
            21: 'Automixer Output'
        }

        ValueStateValues = {
            'MANUAL': 'Manual',
            'GAINSHARE': 'Gain Share',
            'GATING': 'Gating'
        }

        qualifier = {'Channel': ChannelStates[int(match.group(1).decode())]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerMode', value, qualifier)

    def SetAutomixerOffAttenuation(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Automixer Output': '21'
        }

        if qualifier['Channel'] in ChannelStates and -110 <= value <= -3:
            AutomixerOffAttenuationCmdString = '< SET {} AUTOMXR_OFF_ATT {:03d} >'.format(ChannelStates[qualifier['Channel']], int(value + 110))
            self.__SetHelper('AutomixerOffAttenuation', AutomixerOffAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomixerOffAttenuation')

    def UpdateAutomixerOffAttenuation(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Automixer Output': '21'
        }

        if qualifier['Channel'] in ChannelStates:
            AutomixerOffAttenuationCmdString = '< GET {} AUTOMXR_OFF_ATT >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AutomixerOffAttenuation', AutomixerOffAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerOffAttenuation')

    def __MatchAutomixerOffAttenuation(self, match, tag):

        ChannelStates = {
            0: 'All Channels',
            21: 'Automixer Output'
        }

        qualifier = {'Channel': ChannelStates[int(match.group(1).decode())]}
        value = int(match.group(2).decode()) - 110.0
        if -110 <= value <= -3:
            self.WriteStatus('AutomixerOffAttenuation', value, qualifier)

    def SetAutomixerPostGateMute(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Automixer Output': '21'
        }

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            AutomixerPostGateMuteCmdString = '< SET {0} AUTOMXR_MUTE {1} >'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('AutomixerPostGateMute', AutomixerPostGateMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomixerPostGateMute')

    def UpdateAutomixerPostGateMute(self, value, qualifier):

        ChannelStates = {
            'All Channels': '00',
            'Automixer Output': '21'
        }

        if qualifier['Channel'] in ChannelStates:
            AutomixerPostGateMuteCmdString = '< GET {} AUTOMXR_MUTE >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AutomixerPostGateMute', AutomixerPostGateMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerPostGateMute')

    def __MatchAutomixerPostGateMute(self, match, tag):

        ChannelStates = {
            0: 'All Channels',
            21: 'Automixer Output'
        }

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        qualifier = {'Channel': ChannelStates[int(match.group(1).decode())]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerPostGateMute', value, qualifier)

    def UpdateCallStatus(self, value, qualifier):

        CallStatusCmdString = '< GET ONHOOK_STATE >'
        self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)

    def __MatchCallStatus(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On Hook',
            'OFF' : 'Off Hook'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CallStatus', value, None)

    def SetCallStatusMode(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'ON',
            'Disable' : 'OFF'
        }

        if value in ValueStateValues:
            CallStatusModeCmdString = '< SET ONHOOK_ENABLE {} >'.format(ValueStateValues[value])
            self.__SetHelper('CallStatusMode', CallStatusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallStatusMode')

    def UpdateCallStatusMode(self, value, qualifier):

        CallStatusModeCmdString = '< GET ONHOOK_ENABLE >'
        self.__UpdateHelper('CallStatusMode', CallStatusModeCmdString, value, qualifier)

    def __MatchCallStatusMode(self, match, tag):

        ValueStateValues = {
            'ON'  : 'Enable',
            'OFF' : 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CallStatusMode', value, None)

    def SetDeviceAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            DeviceAudioMuteCmdString = '< SET DEVICE_AUDIO_MUTE {} >'.format(ValueStateValues[value])
            self.__SetHelper('DeviceAudioMute', DeviceAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceAudioMute')

    def UpdateDeviceAudioMute(self, value, qualifier):

        DeviceAudioMuteCmdString = '< GET DEVICE_AUDIO_MUTE >'
        self.__UpdateHelper('DeviceAudioMute', DeviceAudioMuteCmdString, value, qualifier)

    def __MatchDeviceAudioMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceAudioMute', value, None)

    def SetFlashLights(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            FlashLightsCmdString = '< SET FLASH {} >'.format(ValueStateValues[value])
            self.__SetHelper('FlashLights', FlashLightsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlashLights')

    def UpdateFlashLights(self, value, qualifier):

        FlashLightsCmdString = '< GET FLASH >'
        self.__UpdateHelper('FlashLights', FlashLightsCmdString, value, qualifier)

    def __MatchFlashLights(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FlashLights', value, None)

    def SetMatrixMixerGain(self, value, qualifier):

        InputStates = {
            'Dante Input 1 w/ Mic Processing' : '01', 
            'Dante Input 2 w/ Mic Processing' : '02', 
            'Dante Input 3 w/ Mic Processing' : '03', 
            'Dante Input 4 w/ Mic Processing' : '04', 
            'Dante Input 5 w/ Mic Processing' : '05', 
            'Dante Input 6 w/ Mic Processing' : '06', 
            'Dante Input 7 w/ Mic Processing' : '07', 
            'Dante Input 8 w/ Mic Processing' : '08', 
            'Dante Input 9' : '09',
            'Dante Input 10' : '10',
            'Analog Input 1' : '11', 
            'Analog Input 2' : '12', 
            'USB Input' : '13', 
            'Mobile Input' : '14',
            'Automixer Output' : '21'
        }

        OutputStates = {
            'Dante Output 1' : '15', 
            'Dante Output 2' : '16', 
            'Analog Output 1' : '17', 
            'Analog Output 2' : '18', 
            'USB Output' : '19', 
            'Mobile Output' : '20', 
            'Dante Output 3' : '23', 
            'Dante Output 4' : '24', 
            'Dante Output 5' : '25', 
            'Dante Output 6' : '26', 
            'Dante Output 7' : '27', 
            'Dante Output 8' : '28'
        }

        if qualifier['Input'] in InputStates and qualifier['Output'] in OutputStates and -110 <= value <= 30:
            MatrixMixerGainCmdString = '< SET {} MATRIX_MXR_GAIN {} {:04d} >'.format(InputStates[qualifier['Input']], OutputStates[qualifier['Output']], int((value + 110) * 10))
            self.__SetHelper('MatrixMixerGain', MatrixMixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerGain')

    def UpdateMatrixMixerGain(self, value, qualifier):

        InputStates = {
            'Dante Input 1 w/ Mic Processing' : '01', 
            'Dante Input 2 w/ Mic Processing' : '02', 
            'Dante Input 3 w/ Mic Processing' : '03', 
            'Dante Input 4 w/ Mic Processing' : '04', 
            'Dante Input 5 w/ Mic Processing' : '05', 
            'Dante Input 6 w/ Mic Processing' : '06', 
            'Dante Input 7 w/ Mic Processing' : '07', 
            'Dante Input 8 w/ Mic Processing' : '08', 
            'Dante Input 9' : '09',
            'Dante Input 10' : '10',
            'Analog Input 1' : '11',
            'Analog Input 2' : '12',
            'USB Input' : '13',
            'Mobile Input' : '14',
            'Automixer Output' : '21'
        }

        OutputStates = {
            'Dante Output 1' : '15',
            'Dante Output 2' : '16',
            'Analog Output 1' : '17',
            'Analog Output 2' : '18',
            'USB Output' : '19',
            'Mobile Output' : '20', 
            'Dante Output 3' : '23', 
            'Dante Output 4' : '24', 
            'Dante Output 5' : '25', 
            'Dante Output 6' : '26', 
            'Dante Output 7' : '27', 
            'Dante Output 8' : '28'
        }

        if qualifier['Input'] in InputStates and qualifier['Output'] in OutputStates:
            MatrixMixerGainCmdString = '< GET {} MATRIX_MXR_GAIN {} >'.format(InputStates[qualifier['Input']], OutputStates[qualifier['Output']])
            self.__UpdateHelper('MatrixMixerGain', MatrixMixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerGain')

    def __MatchMatrixMixerGain(self, match, tag):

        InputStates = {
            1 : 'Dante Input 1 w/ Mic Processing',
            2 : 'Dante Input 2 w/ Mic Processing',
            3 : 'Dante Input 3 w/ Mic Processing',
            4 : 'Dante Input 4 w/ Mic Processing',
            5 : 'Dante Input 5 w/ Mic Processing',
            6 : 'Dante Input 6 w/ Mic Processing',
            7 : 'Dante Input 7 w/ Mic Processing',
            8 : 'Dante Input 8 w/ Mic Processing',
            9 : 'Dante Input 9',
            10 : 'Dante Input 10',
            11 : 'Analog Input 1',
            12 : 'Analog Input 2',
            13 : 'USB Input',
            14 : 'Mobile Input',
            21 : 'Automixer Output'
        }

        OutputStates = {
            15 : 'Dante Output 1',
            16 : 'Dante Output 2',
            17 : 'Analog Output 1',
            18 : 'Analog Output 2',
            19 : 'USB Output',
            20 : 'Mobile Output',
            23 : 'Dante Output 3',
            24 : 'Dante Output 4',
            25 : 'Dante Output 5',
            26 : 'Dante Output 6',
            27 : 'Dante Output 7',
            28 : 'Dante Output 8',
        }

        qualifier = {'Input': InputStates[int(match.group(1).decode())], 'Output': OutputStates[int(match.group(2).decode())]}
        value = (int(match.group(3).decode()) / 10) - 110.0
        if -110 <= value <= 30:
            self.WriteStatus('MatrixMixerGain', value, qualifier)

    def SetMatrixMixerRouting(self, value, qualifier):

        InputStates = {
            'Dante Input 1 w/ Mic Processing' : '01', 
            'Dante Input 2 w/ Mic Processing' : '02', 
            'Dante Input 3 w/ Mic Processing' : '03', 
            'Dante Input 4 w/ Mic Processing' : '04', 
            'Dante Input 5 w/ Mic Processing' : '05', 
            'Dante Input 6 w/ Mic Processing' : '06', 
            'Dante Input 7 w/ Mic Processing' : '07', 
            'Dante Input 8 w/ Mic Processing' : '08', 
            'Dante Input 9' : '09',
            'Dante Input 10' : '10',
            'Analog Input 1' : '11', 
            'Analog Input 2' : '12', 
            'USB Input' : '13', 
            'Mobile Input' : '14',
            'Automixer Output' : '21'
        }

        OutputStates = {
            'Dante Output 1' : '15', 
            'Dante Output 2' : '16', 
            'Analog Output 1' : '17', 
            'Analog Output 2' : '18', 
            'USB Output' : '19', 
            'Mobile Output' : '20', 
            'Dante Output 3' : '23', 
            'Dante Output 4' : '24', 
            'Dante Output 5' : '25', 
            'Dante Output 6' : '26', 
            'Dante Output 7' : '27', 
            'Dante Output 8' : '28'
        }

        ValueStateValues = {
            'On' : 'ON',
            'Off' : 'OFF'
        }

        if qualifier['Input'] in InputStates and qualifier['Output'] in OutputStates and value in ValueStateValues:
            MatrixMixerRoutingCmdString = '< SET {0} MATRIX_MXR_ROUTE {1} {2} >'.format(InputStates[qualifier['Input']], OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('MatrixMixerRouting', MatrixMixerRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerRouting')

    def UpdateMatrixMixerRouting(self, value, qualifier):

        InputStates = {
            'Dante Input 1 w/ Mic Processing' : '01', 
            'Dante Input 2 w/ Mic Processing' : '02', 
            'Dante Input 3 w/ Mic Processing' : '03', 
            'Dante Input 4 w/ Mic Processing' : '04', 
            'Dante Input 5 w/ Mic Processing' : '05', 
            'Dante Input 6 w/ Mic Processing' : '06', 
            'Dante Input 7 w/ Mic Processing' : '07', 
            'Dante Input 8 w/ Mic Processing' : '08', 
            'Dante Input 9' : '09',
            'Dante Input 10' : '10',
            'Analog Input 1' : '11',
            'Analog Input 2' : '12',
            'USB Input' : '13',
            'Mobile Input' : '14',
            'Automixer Output' : '21'
        }

        OutputStates = {
            'Dante Output 1' : '15',
            'Dante Output 2' : '16',
            'Analog Output 1' : '17',
            'Analog Output 2' : '18',
            'USB Output' : '19',
            'Mobile Output' : '20', 
            'Dante Output 3' : '23', 
            'Dante Output 4' : '24', 
            'Dante Output 5' : '25', 
            'Dante Output 6' : '26', 
            'Dante Output 7' : '27', 
            'Dante Output 8' : '28'
        }

        if qualifier['Input'] in InputStates and qualifier['Output'] in OutputStates:
            MatrixMixerRoutingCmdString = '< GET {} MATRIX_MXR_ROUTE {} >'.format(InputStates[qualifier['Input']], OutputStates[qualifier['Output']])
            self.__UpdateHelper('MatrixMixerRouting', MatrixMixerRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerRouting')

    def __MatchMatrixMixerRouting(self, match, tag):

        InputStates = {
            1 : 'Dante Input 1 w/ Mic Processing',
            2 : 'Dante Input 2 w/ Mic Processing',
            3 : 'Dante Input 3 w/ Mic Processing',
            4 : 'Dante Input 4 w/ Mic Processing',
            5 : 'Dante Input 5 w/ Mic Processing',
            6 : 'Dante Input 6 w/ Mic Processing',
            7 : 'Dante Input 7 w/ Mic Processing',
            8 : 'Dante Input 8 w/ Mic Processing',
            9 : 'Dante Input 9',
            10 : 'Dante Input 10',
            11 : 'Analog Input 1',
            12 : 'Analog Input 2',
            13 : 'USB Input',
            14 : 'Mobile Input',
            21 : 'Automixer Output'
        }

        OutputStates = {
            15 : 'Dante Output 1',
            16 : 'Dante Output 2',
            17 : 'Analog Output 1',
            18 : 'Analog Output 2',
            19 : 'USB Output',
            20 : 'Mobile Output',
            23 : 'Dante Output 3',
            24 : 'Dante Output 4',
            25 : 'Dante Output 5',
            26 : 'Dante Output 6',
            27 : 'Dante Output 7',
            28 : 'Dante Output 8',
        }

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        qualifier = {'Input': InputStates[int(match.group(1).decode())], 'Output': OutputStates[int(match.group(2).decode())]}
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MatrixMixerRouting', value, qualifier)

    def SetPreset(self, value, qualifier):

        if 1 <= int(value) <= 10:
            PresetCmdString = '< SET PRESET {:02d} >'.format(int(value))
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = '< GET PRESET >'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('Preset', value, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = '< SET REBOOT >'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

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

    def __MatchError(self, match, tag):

        self.counter = 0

        self.Error(['Error occurred'])

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
                    except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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