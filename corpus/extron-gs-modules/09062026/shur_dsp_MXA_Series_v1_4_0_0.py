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
        self.Models = {
            'MXA310': self.shur_25_2299_310,
            'MXA910': self.shur_25_2299_910
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveMicChannels': { 'Status': {}},
            'AudioGain': {'Parameters':['Channel'], 'Status': {}},
            'AudioGainPostgate': {'Parameters':['Channel'], 'Status': {}},
            'AudioPeakLevelStatus': {'Parameters':['Channel'], 'Status': {}},
            'AudioRMSLevelStatus': {'Parameters':['Channel'], 'Status': {}},
            'AutomixerGateOutStatus': {'Parameters':['Channel'], 'Status': {}},
            'ChannelMute': {'Parameters':['Channel'], 'Status': {}},
            'ChannelMuteAllChannels': { 'Status': {}},
            'DeviceMute': { 'Status': {}},
            'ExternalSwitchOutState': { 'Status': {}},
            'IdentifyMicrophone': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'LEDMutedColor': { 'Status': {}},
            'LEDMutedState': { 'Status': {}},
            'LEDUnmutedColor': { 'Status': {}},
            'LEDUnmutedState': { 'Status': {}},
            'LEDPower': { 'Status': {}},
            'LobeBeamHeight': {'Parameters':['Channel'], 'Status': {}},
            'LobeBeamSteering': {'Parameters':['Axis','Channel'], 'Status': {}},
            'LobeBeamWidth': {'Parameters':['Channel'], 'Status': {}},
            'ModelNumber': { 'Status': {}},
            'MuteButtonLEDState': { 'Status': {}},
            'MuteButtonStatus': { 'Status': {}},
            'OutputClipStatus': {'Parameters':['Channel'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'RingLEDPower': { 'Status': {}},
            'SegmentLEDPower': {'Parameters':['Channel'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP NUM_ACTIVE_MICS ([1-8]) >'), self.__MatchActiveMicChannels, None)
            self.AddMatchString(re.compile(b'< REP ([1-9]) AUDIO_GAIN_HI_RES (\d{4}) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-8]) AUDIO_GAIN_POSTGATE (\d{4}) >'), self.__MatchAudioGainPostgate, None)
            self.AddMatchString(re.compile(b'< REP ([1-9]) AUDIO_IN_PEAK_LVL (\d{3}) >'), self.__MatchAudioPeakLevelStatus, None)
            self.AddMatchString(re.compile(b'< REP ([1-9]) AUDIO_IN_RMS_LVL (\d{3}) >'), self.__MatchAudioRMSLevelStatus, None)
            self.AddMatchString(re.compile(b'< REP ([1-9]) AUDIO_MUTE (ON|OFF) >'), self.__MatchChannelMute, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_AUDIO_MUTE (ON|OFF) >'), self.__MatchDeviceMute, None)
            self.AddMatchString(re.compile(b'< REP EXT_SWITCH_OUT_STATE (ON|OFF) >'), self.__MatchExternalSwitchOutState, None)
            self.AddMatchString(re.compile(b'< REP FLASH (ON|OFF) >'), self.__MatchIdentifyMicrophone, None)
            self.AddMatchString(re.compile(b'< REP ([0-9]) AUTOMIX_GATE_OUT_EXT_SIG (ON|OFF) >'), self.__MatchAutomixerGateOutStatus, None)
            self.AddMatchString(re.compile(b'< REP LED_BRIGHTNESS ([0-5]) >'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'< REP LED_COLOR_MUTED (RED|ORANGE|GOLD|YELLOW|YELLOWGREEN|GREEN|TURQUOISE|POWDERBLUE|CYAN|SKYBLUE|BLUE|PURPLE|LIGHTPURPLE|VIOLET|ORCHID|PINK|WHITE) >', re.I), self.__MatchLEDMutedColor, None)
            self.AddMatchString(re.compile(b'< REP LED_COLOR_UNMUTED (RED|ORANGE|GOLD|YELLOW|YELLOWGREEN|GREEN|TURQUOISE|POWDERBLUE|CYAN|SKYBLUE|BLUE|PURPLE|LIGHTPURPLE|VIOLET|ORCHID|PINK|WHITE) >', re.I), self.__MatchLEDUnmutedColor, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_MUTED (ON|FLASHING|OFF) >', re.I), self.__MatchLEDMutedState, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_UNMUTED (ON|FLASHING|OFF) >', re.I), self.__MatchLEDUnmutedState, None)
            self.AddMatchString(re.compile(b'< REP DEV_LED_IN_STATE (ON|OFF) >'), self.__MatchLEDPower, None)
            self.AddMatchString(re.compile(b'< REP ([1-9]) BEAM_Z (\d{1,4}) >'), self.__MatchLobeBeamHeight, None)
            self.AddMatchString(re.compile(b'< REP ([1-9]) BEAM_(X|Y) (\d{1,4}) >'), self.__MatchLobeBeamSteering, None)
            self.AddMatchString(re.compile(b'< REP ([1-9]) BEAM_W (WIDE|MEDIUM|NARROW) >'), self.__MatchLobeBeamWidth, None)
            self.AddMatchString(re.compile(b'< REP MODEL (.+?) >'), self.__MatchModelNumber, None)
            self.AddMatchString(re.compile(b'< REP MUTE_BUTTON_LED_STATE (ON|OFF) >'), self.__MatchMuteButtonLEDState, None)
            self.AddMatchString(re.compile(b'< REP MUTE_BUTTON_STATUS (ON|OFF) >'), self.__MatchMuteButtonStatus, None)
            self.AddMatchString(re.compile(b'< REP ([0-9]) AUDIO_OUT_CLIP_INDICATOR (ON|OFF) >'), self.__MatchOutputClipStatus, None)
            self.AddMatchString(re.compile(b'< REP PRESET (\d{2}) >'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'< REP ([1-4]) CHAN_LED_IN_STATE (ON|OFF) >'), self.__MatchSegmentLEDPower, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)

    def UpdateActiveMicChannels(self, value, qualifier):

        ActiveMicChannelsCmdString = '< GET NUM_ACTIVE_MICS >'
        self.__UpdateHelper('ActiveMicChannels', ActiveMicChannelsCmdString, value, qualifier)

    def __MatchActiveMicChannels(self, match, tag):

        value = self.MicChannelStatusStates[match.group(1).decode()]
        self.WriteStatus('ActiveMicChannels', value, None)

    def SetAudioGain(self, value, qualifier):

        temp = round(value, 1)

        if -110 <= temp <= 30 and qualifier['Channel'] in self.ChannelStates:
            AudioGainCmdString = '< SET {0} AUDIO_GAIN_HI_RES {1:04} >'.format(self.ChannelStates[qualifier['Channel']], int(temp * 10) + 1100)
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        if qualifier['Channel'] in self.ChannelStates:
            AudioGainCmdString = '< GET {0} AUDIO_GAIN_HI_RES >'.format(self.ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = self.ChannelStatusStates[match.group(1).decode()]
        value = (int(match.group(2).decode()) - 1100) / 10
        if -110 <= value <= 30:
            self.WriteStatus('AudioGain', value, qualifier)

    def SetAudioGainPostgate(self, value, qualifier):

        temp = round(value, 1)

        if qualifier['Channel'] in self.AudioGainChannels and -110 <= temp <= 30:
            AudioGainPostgateCmdString = '< SET {} AUDIO_GAIN_POSTGATE {:04} >'.format(self.ChannelStates[qualifier['Channel']], int(temp * 10) + 1100)
            self.__SetHelper('AudioGainPostgate', AudioGainPostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainPostgate')

    def UpdateAudioGainPostgate(self, value, qualifier):

        if qualifier['Channel'] in self.AudioGainChannels:
            AudioGainPostgateCmdString = '< GET {} AUDIO_GAIN_POSTGATE >'.format(self.ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioGainPostgate', AudioGainPostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGainPostgate')

    def __MatchAudioGainPostgate(self, match, tag):

        qualifier = {
            'Channel': self.AudioGainChannels[match.group(1).decode()]
        }

        value = (int(match.group(2).decode()) - 1100) / 10
        if -110 <= value <= 30:
            self.WriteStatus('AudioGainPostgate', value, qualifier)

    def UpdateAudioPeakLevelStatus(self, value, qualifier):

        AudioPeakLevelStatusCmdString = '< GET 0 AUDIO_IN_PEAK_LVL >'
        self.__UpdateHelper('AudioPeakLevelStatus', AudioPeakLevelStatusCmdString, value, qualifier)

    def __MatchAudioPeakLevelStatus(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = self.ChannelStatusStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('AudioPeakLevelStatus', value, qualifier)

    def UpdateAudioRMSLevelStatus(self, value, qualifier):

        AudioRMSLevelCmdString = '< GET 0 AUDIO_IN_RMS_LVL >'
        self.__UpdateHelper('AudioRMSLevelStatus', AudioRMSLevelCmdString, value, qualifier)

    def __MatchAudioRMSLevelStatus(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = self.ChannelStatusStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('AudioRMSLevelStatus', value, qualifier)

    def SetChannelMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        if qualifier['Channel'] in self.ChannelStates:
            ChannelAudioMuteCmdString = '< SET {0} AUDIO_MUTE {1} >'.format(self.ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('ChannelMute', ChannelAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMute')

    def UpdateChannelMute(self, value, qualifier):

        ChannelAudioMuteCmdString = '< GET 0 AUDIO_MUTE >'
        self.__UpdateHelper('ChannelMute', ChannelAudioMuteCmdString, value, qualifier)

    def __MatchChannelMute(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = self.ChannelStatusStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ChannelMute', value, qualifier)

    def SetChannelMuteAllChannels(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        ChannelAudioMuteAllChannelsCmdString = '< SET 0 AUDIO_MUTE {0} >'.format(ValueStateValues[value])
        self.__SetHelper('ChannelMuteAllChannels', ChannelAudioMuteAllChannelsCmdString, value, qualifier)
    
    def SetDeviceMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        DeviceAudioMuteCmdString = '< SET DEVICE_AUDIO_MUTE {0} >'.format(ValueStateValues[value])
        self.__SetHelper('DeviceMute', DeviceAudioMuteCmdString, value, qualifier)

    def UpdateDeviceMute(self, value, qualifier):

        DeviceAudioMuteCmdString = '< GET DEVICE_AUDIO_MUTE >'
        self.__UpdateHelper('DeviceMute', DeviceAudioMuteCmdString, value, qualifier)

    def __MatchDeviceMute(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceMute', value, None)

    def UpdateExternalSwitchOutState(self, value, qualifier):

        ExternalSwitchOutStateCmdString = '< GET EXT_SWITCH_OUT_STATE >'
        self.__UpdateHelper('ExternalSwitchOutState', ExternalSwitchOutStateCmdString, value, qualifier)

    def __MatchExternalSwitchOutState(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExternalSwitchOutState', value, None)

    def SetIdentifyMicrophone(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        IdentifyMicrophoneCmdString = '< SET FLASH {0} >'.format(ValueStateValues[value])
        self.__SetHelper('IdentifyMicrophone', IdentifyMicrophoneCmdString, value, qualifier)

    def UpdateIdentifyMicrophone(self, value, qualifier):

        IdentifyMicrophoneCmdString = '< GET FLASH >'
        self.__UpdateHelper('IdentifyMicrophone', IdentifyMicrophoneCmdString, value, qualifier)

    def __MatchIdentifyMicrophone(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IdentifyMicrophone', value, None)

    def UpdateAutomixerGateOutStatus(self, value, qualifier):

        GateOutStatusCmdString = '< GET 0 AUTOMIX_GATE_OUT_EXT_SIG >'
        self.__UpdateHelper('AutomixerGateOutStatus', GateOutStatusCmdString, value, qualifier)

    def __MatchAutomixerGateOutStatus(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = self.ChannelStatusStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerGateOutStatus', value, qualifier)

    def SetLEDBrightness(self, value, qualifier):

        ValueStateValues = {
            'Disabled': '0',
            '20%'     : '1',
            '40%'     : '2',
            '60%'     : '3',
            '80%'     : '4',
            '100%'    : '5'
        }

        LEDBrightnessCmdString = '< SET LED_BRIGHTNESS {0} >'.format(ValueStateValues[value])
        self.__SetHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)

    def UpdateLEDBrightness(self, value, qualifier):

        LEDBrightnessCmdString = '< GET LED_BRIGHTNESS >'
        self.__UpdateHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)

    def __MatchLEDBrightness(self, match, tag):

        ValueStateValues = {
            '0': 'Disabled',
            '1': '20%',
            '2': '40%',
            '3': '60%',
            '4': '80%',
            '5': '100%'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LEDBrightness', value, None)

    def SetLEDMutedColor(self, value, qualifier):

        ValueStateValues = {
            'Red':          'RED',
            'Orange':       'ORANGE',
            'Gold':         'GOLD',
            'Yellow':       'YELLOW',
            'Yellow Green': 'YELLOWGREEN',
            'Green':        'GREEN',
            'Turquoise':    'TURQUOISE',
            'Powder Blue':  'POWDERBLUE',
            'Cyan':         'CYAN',
            'Sky Blue':     'SKYBLUE',
            'Blue':         'BLUE',
            'Purple':       'PURPLE',
            'Light Purple': 'LIGHTPURPLE',
            'Violet':       'VIOLET',
            'Orchid':       'ORCHID',
            'Pink':         'PINK',
            'White':        'WHITE'
        }

        if value in ValueStateValues:
            LEDMutedColorCmdString = '< SET LED_COLOR_MUTED {} >'.format(ValueStateValues[value])
            self.__SetHelper('LEDMutedColor', LEDMutedColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDMutedColor')

    def UpdateLEDMutedColor(self, value, qualifier):

        LEDMutedColorCmdString = '< GET LED_COLOR_MUTED >'
        self.__UpdateHelper('LEDMutedColor', LEDMutedColorCmdString, value, qualifier)

    def __MatchLEDMutedColor(self, match, tag):

        ValueStateValues = {
            'RED':          'Red',
            'ORANGE':       'Orange',
            'GOLD':         'Gold',
            'YELLOW':       'Yellow',
            'YELLOWGREEN':  'Yellow Green',
            'GREEN':        'Green',
            'TURQUOISE':    'Turquoise',
            'POWDERBLUE':   'Powder Blue',
            'CYAN':         'Cyan',
            'SKYBLUE':      'Sky Blue',
            'BLUE':         'Blue',
            'PURPLE':       'Purple',
            'LIGHTPURPLE':  'Light Purple',
            'VIOLET':       'Violet',
            'ORCHID':       'Orchid',
            'PINK':         'Pink',
            'WHITE':        'White'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('LEDMutedColor', value, None)

    def SetLEDUnmutedColor(self, value, qualifier):

        ValueStateValues = {
            'Red':          'RED',
            'Orange':       'ORANGE',
            'Gold':         'GOLD',
            'Yellow':       'YELLOW',
            'Yellow Green': 'YELLOWGREEN',
            'Green':        'GREEN',
            'Turquoise':    'TURQUOISE',
            'Powder Blue':  'POWDERBLUE',
            'Cyan':         'CYAN',
            'Sky Blue':     'SKYBLUE',
            'Blue':         'BLUE',
            'Purple':       'PURPLE',
            'Light Purple': 'LIGHTPURPLE',
            'Violet':       'VIOLET',
            'Orchid':       'ORCHID',
            'Pink':         'PINK',
            'White':        'WHITE'
        }

        if value in ValueStateValues:
            LEDUnmutedColorCmdString = '< SET LED_COLOR_UNMUTED {} >'.format(ValueStateValues[value])
            self.__SetHelper('LEDUnmutedColor', LEDUnmutedColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDUnmutedColor')

    def UpdateLEDUnmutedColor(self, value, qualifier):

        LEDUnmutedColorCmdString = '< GET LED_COLOR_UNMUTED >'
        self.__UpdateHelper('LEDUnmutedColor', LEDUnmutedColorCmdString, value, qualifier)

    def __MatchLEDUnmutedColor(self, match, tag):

        ValueStateValues = {
            'RED':          'Red',
            'ORANGE':       'Orange',
            'GOLD':         'Gold',
            'YELLOW':       'Yellow',
            'YELLOWGREEN':  'Yellow Green',
            'GREEN':        'Green',
            'TURQUOISE':    'Turquoise',
            'POWDERBLUE':   'Powder Blue',
            'CYAN':         'Cyan',
            'SKYBLUE':      'Sky Blue',
            'BLUE':         'Blue',
            'PURPLE':       'Purple',
            'LIGHTPURPLE':  'Light Purple',
            'VIOLET':       'Violet',
            'ORCHID':       'Orchid',
            'PINK':         'Pink',
            'WHITE':        'White'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('LEDUnmutedColor', value, None)

    def SetLEDMutedState(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Flashing',
            'Off'
        ]

        if value in ValueStateValues:
            LEDMutedStateCmdString = '< SET LED_STATE_MUTED {} >'.format(value.upper())
            self.__SetHelper('LEDMutedState', LEDMutedStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDMutedState')

    def UpdateLEDMutedState(self, value, qualifier):

        LEDMutedStateCmdString = '< GET LED_STATE_MUTED >'
        self.__UpdateHelper('LEDMutedState', LEDMutedStateCmdString, value, qualifier)

    def __MatchLEDMutedState(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('LEDMutedState', value, None)

    def SetLEDUnmutedState(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Flashing',
            'Off'
        ]

        if value in ValueStateValues:
            LEDUnmutedStateCmdString = '< SET LED_STATE_UNMUTED {} >'.format(value.upper())
            self.__SetHelper('LEDUnmutedState', LEDUnmutedStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDUnmutedState')

    def UpdateLEDUnmutedState(self, value, qualifier):

        LEDUnmutedStateCmdString = '< GET LED_STATE_UNMUTED >'
        self.__UpdateHelper('LEDUnmutedState', LEDUnmutedStateCmdString, value, qualifier)

    def __MatchLEDUnmutedState(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('LEDUnmutedState', value, None)

    def SetLEDPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        LEDPowerCmdString = '< SET DEV_LED_IN_STATE {0} >'.format(ValueStateValues[value])
        self.__SetHelper('LEDPower', LEDPowerCmdString, value, qualifier)

    def UpdateLEDPower(self, value, qualifier):

        LEDPowerCmdString = '< GET DEV_LED_IN_STATE >'
        self.__UpdateHelper('LEDPower', LEDPowerCmdString, value, qualifier)

    def UpdateMuteButtonLEDState(self, value, qualifier):

        MuteButtonLEDStateCmdString = '< GET MUTE_BUTTON_LED_STATE >'
        self.__UpdateHelper('MuteButtonLEDState', MuteButtonLEDStateCmdString, value, qualifier)

    def __MatchMuteButtonLEDState(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteButtonLEDState', value, None)

    def UpdateModelNumber(self, value, qualifier):

        ModelNumberCmdString = '< GET MODEL >'
        self.__UpdateHelper('ModelNumber', ModelNumberCmdString, value, qualifier)

    def __MatchModelNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ModelNumber', value, None)

    def UpdateMuteButtonStatus(self, value, qualifier):

        MuteButtonStatusCmdString = '< GET MUTE_BUTTON_STATUS >'
        self.__UpdateHelper('MuteButtonStatus', MuteButtonStatusCmdString, value, qualifier)

    def __MatchMuteButtonStatus(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteButtonStatus', value, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = '< SET REBOOT >'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)
    
    def UpdateOutputClipStatus(self, value, qualifier):

        OutputClipStatusCmdString = '< GET 0 AUDIO_OUT_CLIP_INDICATOR >'
        self.__UpdateHelper('OutputClipStatus', OutputClipStatusCmdString, value, qualifier)

    def __MatchOutputClipStatus(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = self.ChannelStatusStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputClipStatus', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10': '10'
        }

        RecallPresetCmdString = '< SET PRESET {0} >'.format(ValueStateValues[value])
        self.__SetHelper('PresetRecall', RecallPresetCmdString, value, qualifier)

    def UpdatePresetRecall(self, value, qualifier):

        RecallPresetCmdString = '< GET PRESET >'
        self.__UpdateHelper('PresetRecall', RecallPresetCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        ValueStateValues = {
            '00': 'No Preset',
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7',
            '08': '8',
            '09': '9',
            '10': '10'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresetRecall', value, None)

    def SetRingLEDPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        RingLEDPowerCmdString = '< SET DEV_LED_IN_STATE {0} >'.format(ValueStateValues[value])
        self.__SetHelper('RingLEDPower', RingLEDPowerCmdString, value, qualifier)

    def UpdateRingLEDPower(self, value, qualifier):

        RingLEDPowerCmdString = '< GET DEV_LED_IN_STATE >'
        self.__UpdateHelper('RingLEDPower', RingLEDPowerCmdString, value, qualifier)

    def __MatchLEDPower(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        if self.ModelNo == '910':
            self.WriteStatus('LEDPower', value, None)
        elif self.ModelNo == '310':
            self.WriteStatus('RingLEDPower', value, None)

    def SetLobeBeamHeight(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
        }

        if 0 <= value <= 914 and qualifier['Channel'] in ChannelStates:
            LobeBeamHeightCmdString = '< SET {0} BEAM_Z {1:03} >'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('LobeBeamHeight', LobeBeamHeightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLobeBeamHeight')

    def UpdateLobeBeamHeight(self, value, qualifier):

        LobeBeamHeightCmdString = '< GET 0 BEAM_Z >'
        self.__UpdateHelper('LobeBeamHeight', LobeBeamHeightCmdString, value, qualifier)
   
    def __MatchLobeBeamHeight(self, match, tag):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('LobeBeamHeight', value, qualifier)

    def SetLobeBeamSteering(self, value, qualifier):

        AxisStates = {
            'X': 'BEAM_X',
            'Y': 'BEAM_Y'
        }

        ChannelStates = {
            'All Channels' : '0', 
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            'Automix Output': '9'
        }

        temp = value + 1524
        if 0 <= temp <= 3048 and qualifier['Axis'] in AxisStates and qualifier['Channel'] in ChannelStates:
            LobeBeamSteeringCmdString = '< SET {0} {1} {2:04} >'.format(ChannelStates[qualifier['Channel']], AxisStates[qualifier['Axis']], temp)
            self.__SetHelper('LobeBeamSteering', LobeBeamSteeringCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLobeBeamSteering')

    def UpdateLobeBeamSteering(self, value, qualifier):

        AxisStates = {
            'X': 'BEAM_X',
            'Y': 'BEAM_Y'
        }

        if qualifier['Axis'] in AxisStates:
            LobeBeamSteeringCmdString = '< GET 0 {0} >'.format(AxisStates[qualifier['Axis']])
            self.__UpdateHelper('LobeBeamSteering', LobeBeamSteeringCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLobeBeamSteering')

    def __MatchLobeBeamSteering(self, match, tag):

        AxisStates = {
            'X': 'X',
            'Y': 'Y'
        }

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        qualifier['Axis'] = AxisStates[match.group(2).decode()]
        value = int(match.group(3).decode()) - 1524
        self.WriteStatus('LobeBeamSteering', value, qualifier)

    def SetLobeBeamWidth(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
        }

        ValueStateValues = {
            'Wide'  : 'WIDE',
            'Medium': 'MEDIUM',
            'Narrow': 'NARROW'
        }

        if qualifier['Channel'] in ChannelStates:
            LobeBeamWidthCmdString = '< SET {0} BEAM_W {1} >'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('LobeBeamWidth', LobeBeamWidthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLobeBeamWidth')

    def UpdateLobeBeamWidth(self, value, qualifier):

        LobeBeamWidthCmdString = '< GET 0 BEAM_W >'
        self.__UpdateHelper('LobeBeamWidth', LobeBeamWidthCmdString, value, qualifier)

    def __MatchLobeBeamWidth(self, match, tag):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
        }

        ValueStateValues = {
            'WIDE'  : 'Wide',
            'MEDIUM': 'Medium',
            'NARROW': 'Narrow'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LobeBeamWidth', value, qualifier)
    
    def SetSegmentLEDPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        if 1 <= int(qualifier['Channel']) <= 4:
            SegmentLEDPowerCmdString = '< SET {0} CHAN_LED_IN_STATE {1} >'.format(qualifier['Channel'], ValueStateValues[value])
            self.__SetHelper('SegmentLEDPower', SegmentLEDPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSegmentLEDPower')

    def UpdateSegmentLEDPower(self, value, qualifier):

        SegmentLEDPowerCmdString = '< GET 0 CHAN_LED_IN_STATE >'
        self.__UpdateHelper('SegmentLEDPower', SegmentLEDPowerCmdString, value, qualifier)

    def __MatchSegmentLEDPower(self, match, tag):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SegmentLEDPower', value, qualifier)

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
        value = match.group(0).decode()
        self.Error([value])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def shur_25_2299_310(self):

        self.ModelNo = '310'

        self.AudioGainChannels = {
            '1'              : '1',
            '2'              : '2',
            '3'              : '3',
            '4'              : '4',
        }

        self.ChannelStates = {
            '1'              : '1',
            '2'              : '2',
            '3'              : '3',
            '4'              : '4',
            'Automix Output' : '5'
        }

        self.ChannelStatusStates = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : 'Automix Output'
        }

        self.MicChannelStatusStates = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
        }
        
    def shur_25_2299_910(self):

        self.ModelNo = '910'

        self.AudioGainChannels = {
            '1'              : '1',
            '2'              : '2',
            '3'              : '3',
            '4'              : '4',
            '5'              : '5',
            '6'              : '6',
            '7'              : '7',
            '8'              : '8',
        }

        self.ChannelStates = {
            '1'              : '1',
            '2'              : '2',
            '3'              : '3',
            '4'              : '4',
            '5'              : '5',
            '6'              : '6',
            '7'              : '7',
            '8'              : '8',
            'Automix Output' : '9'
        }

        self.ChannelStatusStates = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8',
            '9' : 'Automix Output'
        }

        self.MicChannelStatusStates = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8',
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()