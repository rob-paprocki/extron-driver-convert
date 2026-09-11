# Copyright 2026, Extron. All rights reserved.

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
            'ActiveMicChannels': { 'Status': {}},
            'ArrayGroupStatus': {'Parameters':['MAC Address'], 'Status': {}},
            'AudioGain': {'Parameters':['Channel'], 'Status': {}},
            'AudioGainPostgate': {'Parameters':['Channel'], 'Status': {}},
            'AudioPeakLevelStatus': {'Parameters':['Channel'], 'Status': {}},
            'AudioRMSLevelStatus': {'Parameters':['Channel'], 'Status': {}},
            'AutomaticCoverage': { 'Status': {}},
            'AutomixerGateOutStatus': {'Parameters':['Channel'], 'Status': {}},
            'ChannelMute': {'Parameters':['Channel'], 'Status': {}},
            'ChannelMuteAllChannels': { 'Status': {}},
            'ChannelMutePostgate': {'Parameters':['Channel'], 'Status': {}},
            'CoverageAreaAutomixerGateOut': {'Parameters':['Coverage Area'], 'Status': {}},
            'CoverageAreaGain': {'Parameters':['Coverage Area'], 'Status': {}},
            'CoverageAreaMeterRate': { 'Status': {}},
            'CoverageAreaMute': {'Parameters':['Coverage Area'], 'Status': {}},
            'DeviceMute': { 'Status': {}},
            'IdentifyMicrophone': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'LEDMutedColor': { 'Status': {}},
            'LEDMutedState': { 'Status': {}},
            'LEDUnmutedColor': { 'Status': {}},
            'LEDUnmutedState': { 'Status': {}},
            'LEDPower': { 'Status': {}},
            'ModelNumber': { 'Status': {}},
            'OutputClipStatus': {'Parameters':['Channel'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'TalkerPositionStatus': { 'Status': {}}
        }

        self.configuredArrayGroups = []

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP NUM_ACTIVE_MICS (\d+) >'), self.__MatchActiveMicChannels, None)
            self.AddMatchString(re.compile(b'< REP ARRAY_GROUP_STATUS OFF >'), self.__MatchArrayGroupStatus, 'Off')
            self.AddMatchString(re.compile(b'< REP ARRAY_GROUP_STATUS((?: [\dA-F:]{17} (?:OK|CONNECTION_ERROR|PROTOCOL_ERROR|INCOMPATIBLE|TOO_FAR|OFF)){1,4}) >'), self.__MatchArrayGroupStatus, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-9]) AUDIO_GAIN_HI_RES (\d+) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-8]) AUDIO_GAIN_POSTGATE (\d+) >'), self.__MatchAudioGainPostgate, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-9]) AUDIO_IN_PEAK_LVL (\d{3}) >'), self.__MatchAudioPeakLevelStatus, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-9]) AUDIO_IN_RMS_LVL (\d{3}) >'), self.__MatchAudioRMSLevelStatus, None)
            self.AddMatchString(re.compile(b'< REP AUTO_COVERAGE (ON|OFF) >', re.I), self.__MatchAutomaticCoverage, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-8]) AUTOMIX_GATE_OUT_EXT_SIG (ON|OFF) >', re.I), self.__MatchAutomixerGateOutStatus, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-9]) AUDIO_MUTE (ON|OFF) >', re.I), self.__MatchChannelMute, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-8]) AUDIO_MUTE_POSTGATE (ON|OFF) >', re.I), self.__MatchChannelMutePostgate, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-8]) AUTOMIX_GATE_OUT_CA (ON|OFF) >', re.I), self.__MatchCoverageAreaAutomixerGateOut, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-8]) CA_GAIN (\d+) >'), self.__MatchCoverageAreaGain, None)
            self.AddMatchString(re.compile(b'< REP CA_METER_RATE (\d+) >'), self.__MatchCoverageAreaMeterRate, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-8]) CA_MUTE (ON|OFF) >', re.I), self.__MatchCoverageAreaMute, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_AUDIO_MUTE (ON|OFF) >', re.I), self.__MatchDeviceMute, None)
            self.AddMatchString(re.compile(b'< REP FLASH (ON|OFF) >', re.I), self.__MatchIdentifyMicrophone, None)
            self.AddMatchString(re.compile(b'< REP LED_BRIGHTNESS ([0-5]) >'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'< REP DEV_LED_IN_STATE (ON|OFF) >', re.I), self.__MatchLEDPower, None)
            self.AddMatchString(re.compile(b'< REP LED_COLOR_MUTED (RED|ORANGE|GOLD|YELLOW|YELLOWGREEN|GREEN|TURQUOISE|POWDERBLUE|CYAN|SKYBLUE|BLUE|PURPLE|LIGHTPURPLE|VIOLET|ORCHID|PINK|WHITE) >', re.I), self.__MatchLEDMutedColor, None)
            self.AddMatchString(re.compile(b'< REP LED_COLOR_UNMUTED (RED|ORANGE|GOLD|YELLOW|YELLOWGREEN|GREEN|TURQUOISE|POWDERBLUE|CYAN|SKYBLUE|BLUE|PURPLE|LIGHTPURPLE|VIOLET|ORCHID|PINK|WHITE) >', re.I), self.__MatchLEDUnmutedColor, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_MUTED (ON|FLASHING|OFF) >', re.I), self.__MatchLEDMutedState, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_UNMUTED (ON|FLASHING|OFF) >', re.I), self.__MatchLEDUnmutedState, None)
            self.AddMatchString(re.compile(b'< REP MODEL \{?(.+?)\}? >'), self.__MatchModelNumber, None)
            self.AddMatchString(re.compile(b'< REP 0?([1-9]) AUDIO_OUT_CLIP_INDICATOR (ON|OFF) >', re.I), self.__MatchOutputClipStatus, None)
            self.AddMatchString(re.compile(b'< REP PRESET (\d+) >'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'< SAMPLE TALKER_POSITIONS([-\d\s]+)>', re.I), self.__MatchTalkerPositionStatus, None)
            self.AddMatchString(re.compile(b'< REP TALKER_POSITION_RATE (\d{1,5}) >', re.I), self.__MatchTalkerPositionStatus, 'Set')

            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)

    def UpdateActiveMicChannels(self, value, qualifier):

        ActiveMicChannelsCmdString = '< GET NUM_ACTIVE_MICS >'
        self.__UpdateHelper('ActiveMicChannels', ActiveMicChannelsCmdString, value, qualifier)

    def __MatchActiveMicChannels(self, match, tag):

        value = int(match.group(1).decode())

        if 0 <= value <= 8:
            self.WriteStatus('ActiveMicChannels', str(value), None)

    def UpdateArrayGroupStatus(self, value, qualifier):

        mac = qualifier['MAC Address']

        if mac:
            if len(self.configuredArrayGroups) < 4:
                self.configuredArrayGroups.append(mac)
            elif mac not in self.configuredArrayGroups:
                self.Error(['Array Group Status: Cannot register more than 4 MAC addresses'])
                return

            ArrayGroupStatusCmdString = '< GET ARRAY_GROUP_STATUS >'
            self.__UpdateHelper('ArrayGroupStatus', ArrayGroupStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateArrayGroupStatus')

    def __MatchArrayGroupStatus(self, match, tag):

        ValueStateValues = {
            'OK':               'OK',
            'CONNECTION_ERROR': 'Connection Error',
            'PROTOCOL_ERROR':   'Protocol Error',
            'INCOMPATIBLE':     'Incompatible',
            'TOO_FAR':          'Too Far',
            'OFF':              'Off'
        }

        mac_list = []
        status_list = []

        if tag != 'Off':
            split = match.group(1).decode().strip().split()
            
            mac_list += split[0::2]
            status_list += split[1::2]
        
        for mac in self.configuredArrayGroups:
            if mac not in mac_list:
                mac_list.append(mac)
                status_list.append('OFF')

        for mac, status in zip(mac_list, status_list):
            if mac in self.configuredArrayGroups:
                self.WriteStatus('ArrayGroupStatus', ValueStateValues[status], {'MAC Address': mac})

    def SetAudioGain(self, value, qualifier):

        ChannelStates = {
            '1':            '01',
            '2':            '02',
            '3':            '03',
            '4':            '04',
            '5':            '05',
            '6':            '06',
            '7':            '07',
            '8':            '08',
            'Automixer':    '09'
        }
        channel = qualifier['Channel']
        temp = round(value, 1)

        if channel in ChannelStates and -110 <= temp <= 30:
            AudioGainCmdString = '< SET {} AUDIO_GAIN_HI_RES {} >'.format(ChannelStates[channel], int(temp * 10) + 1100)
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        ChannelStates = {
            '1':            '01',
            '2':            '02',
            '3':            '03',
            '4':            '04',
            '5':            '05',
            '6':            '06',
            '7':            '07',
            '8':            '08',
            'Automixer':    '09'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            AudioGainCmdString = '< GET {} AUDIO_GAIN_HI_RES >'.format(ChannelStates[channel])
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        ChannelStates = {
            '1'     : '1',
            '2'     : '2',
            '3'     : '3',
            '4'     : '4',
            '5'     : '5',
            '6'     : '6',
            '7'     : '7',
            '8'     : '8',
            '9'     : 'Automixer'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = (int(match.group(2).decode()) - 1100) / 10
        if -110 <= value <= 30:
            self.WriteStatus('AudioGain', value, qualifier)

    def SetAudioGainPostgate(self, value, qualifier):

        channel = int(qualifier['Channel'])
        temp = round(value, 1)

        if 1 <= channel <= 8 and -110 <= temp <= 30:
            AudioGainPostgateCmdString = '< SET {:02d} AUDIO_GAIN_POSTGATE {:04} >'.format(channel, int(temp * 10) + 1100)
            self.__SetHelper('AudioGainPostgate', AudioGainPostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainPostgate')

    def UpdateAudioGainPostgate(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 8:
            AudioGainPostgateCmdString = '< GET {:02d} AUDIO_GAIN_POSTGATE >'.format(channel)
            self.__UpdateHelper('AudioGainPostgate', AudioGainPostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGainPostgate')

    def __MatchAudioGainPostgate(self, match, tag):

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = (int(match.group(2).decode()) - 1100) / 10
        if -110 <= value <= 30:
            self.WriteStatus('AudioGainPostgate', value, qualifier)

    def UpdateAudioPeakLevelStatus(self, value, qualifier):

        AudioPeakLevelStatusCmdString = '< GET 0 AUDIO_IN_PEAK_LVL >'
        self.__UpdateHelper('AudioPeakLevelStatus', AudioPeakLevelStatusCmdString, value, qualifier)

    def __MatchAudioPeakLevelStatus(self, match, tag):

        ChannelStates = {
            '1'     : '1',
            '2'     : '2',
            '3'     : '3',
            '4'     : '4',
            '5'     : '5',
            '6'     : '6',
            '7'     : '7',
            '8'     : '8',
            '9'     : 'Automixer'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('AudioPeakLevelStatus', value, qualifier)

    def UpdateAudioRMSLevelStatus(self, value, qualifier):

        AudioRMSLevelCmdString = '< GET 0 AUDIO_IN_RMS_LVL >'
        self.__UpdateHelper('AudioRMSLevelStatus', AudioRMSLevelCmdString, value, qualifier)

    def __MatchAudioRMSLevelStatus(self, match, tag):

        ChannelStates = {
            '1'     : '1',
            '2'     : '2',
            '3'     : '3',
            '4'     : '4',
            '5'     : '5',
            '6'     : '6',
            '7'     : '7',
            '8'     : '8',
            '9'     : 'Automixer'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('AudioRMSLevelStatus', value, qualifier)

    def SetAutomaticCoverage(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            AutomaticCoverageCmdString = '< SET AUTO_COVERAGE {} >'.format(value.upper())
            self.__SetHelper('AutomaticCoverage', AutomaticCoverageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomaticCoverage')

    def UpdateAutomaticCoverage(self, value, qualifier):

        AutomaticCoverageCmdString = '< GET AUTO_COVERAGE >'
        self.__UpdateHelper('AutomaticCoverage', AutomaticCoverageCmdString, value, qualifier)

    def __MatchAutomaticCoverage(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutomaticCoverage', value, None)

    def UpdateAutomixerGateOutStatus(self, value, qualifier):

        ca = int(qualifier['Channel'])

        if 1 <= ca <= 8:
            AutomixerGateOutStatusCmdString = '< GET {:02d} AUTOMIX_GATE_OUT_EXT_SIG >'.format(ca)
            self.__UpdateHelper('AutomixerGateOutStatus', AutomixerGateOutStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerGateOutStatus')

    def __MatchAutomixerGateOutStatus(self, match, tag):

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = match.group(2).decode().title()
        self.WriteStatus('AutomixerGateOutStatus', value, qualifier)

    def SetChannelMute(self, value, qualifier):

        ChannelStates = {
            '1':            '01',
            '2':            '02',
            '3':            '03',
            '4':            '04',
            '5':            '05',
            '6':            '06',
            '7':            '07',
            '8':            '08',
            'Automixer':    '09'
        }
        channel = qualifier['Channel']

        ValueStateValues = [
            'On',
            'Off'
        ]

        if channel in ChannelStates and value in ValueStateValues:
            ChannelMuteCmdString = '< SET {} AUDIO_MUTE {} >'.format(ChannelStates[channel], value.upper())
            self.__SetHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMute')

    def UpdateChannelMute(self, value, qualifier):

        ChannelStates = {
            '1':            '01',
            '2':            '02',
            '3':            '03',
            '4':            '04',
            '5':            '05',
            '6':            '06',
            '7':            '07',
            '8':            '08',
            'Automixer':    '09'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            ChannelMuteCmdString = '< GET {} AUDIO_MUTE >'.format(ChannelStates[channel])
            self.__UpdateHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelMute')

    def __MatchChannelMute(self, match, tag):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': 'Automixer'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = match.group(2).decode().title()
        self.WriteStatus('ChannelMute', value, qualifier)

    def SetChannelMuteAllChannels(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off': 'OFF'
        }

        ChannelAudioMuteAllChannelsCmdString = '< SET 0 AUDIO_MUTE {0} >'.format(ValueStateValues[value])
        self.__SetHelper('ChannelMuteAllChannels', ChannelAudioMuteAllChannelsCmdString, value, qualifier)

    def SetChannelMutePostgate(self, value, qualifier):

        channel = int(qualifier['Channel'])

        ValueStateValues = [
            'On',
            'Off'
        ]

        if 1 <= channel <= 8 and value in ValueStateValues:
            ChannelMutePostgateCmdString = '< SET {:02d} AUDIO_MUTE_POSTGATE {} >'.format(channel, value.upper())
            self.__SetHelper('ChannelMutePostgate', ChannelMutePostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMutePostgate')

    def UpdateChannelMutePostgate(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 8:
            ChannelMutePostgateCmdString = '< GET {:02d} AUDIO_MUTE_POSTGATE >'.format(channel)
            self.__UpdateHelper('ChannelMutePostgate', ChannelMutePostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelMutePostgate')

    def __MatchChannelMutePostgate(self, match, tag):

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = match.group(2).decode().title()
        self.WriteStatus('ChannelMutePostgate', value, qualifier)

    def UpdateCoverageAreaAutomixerGateOut(self, value, qualifier):

        ca = int(qualifier['Coverage Area'])

        if 1 <= ca <= 8:
            CoverageAreaAutomixerGateOutCmdString = '< GET {:02d} AUTOMIX_GATE_OUT_CA >'.format(ca)
            self.__UpdateHelper('CoverageAreaAutomixerGateOut', CoverageAreaAutomixerGateOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCoverageAreaAutomixerGateOut')

    def __MatchCoverageAreaAutomixerGateOut(self, match, tag):

        qualifier = {
            'Coverage Area': match.group(1).decode()
        }

        value = match.group(2).decode().title()
        self.WriteStatus('CoverageAreaAutomixerGateOut', value, qualifier)

    def SetCoverageAreaGain(self, value, qualifier):

        ca = int(qualifier['Coverage Area'])
        temp = round(value, 1)

        if 1 <= ca <= 8 and -110 <= temp <= 30:
            CoverageAreaGainCmdString = '< SET {:02d} CA_GAIN {:04} >'.format(ca, int(temp * 10) + 1100)
            self.__SetHelper('CoverageAreaGain', CoverageAreaGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCoverageAreaGain')

    def UpdateCoverageAreaGain(self, value, qualifier):

        ca = int(qualifier['Coverage Area'])

        if 1 <= ca <= 8:
            CoverageAreaGainCmdString = '< GET {:02d} CA_GAIN >'.format(ca)
            self.__UpdateHelper('CoverageAreaGain', CoverageAreaGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCoverageAreaGain')

    def __MatchCoverageAreaGain(self, match, tag):

        qualifier = {
            'Coverage Area': match.group(1).decode()
        }

        value = (int(match.group(2).decode()) - 1100) / 10
        if -110 <= value <= 30:
            self.WriteStatus('CoverageAreaGain', value, qualifier)

    def UpdateCoverageAreaMeterRate(self, value, qualifier):

        CoverageAreaMeterRateCmdString = '< GET CA_METER_RATE >'
        self.__UpdateHelper('CoverageAreaMeterRate', CoverageAreaMeterRateCmdString, value, qualifier)

    def __MatchCoverageAreaMeterRate(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 99999:
            self.WriteStatus('CoverageAreaMeterRate', value, None)

    def SetCoverageAreaMute(self, value, qualifier):

        ca = int(qualifier['Coverage Area'])

        ValueStateValues = [
            'On',
            'Off'
        ]

        if 1 <= ca <= 8 and value in ValueStateValues:
            CoverageAreaMuteCmdString = '< SET {:02d} CA_MUTE {} >'.format(ca, value.upper())
            self.__SetHelper('CoverageAreaMute', CoverageAreaMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCoverageAreaMute')

    def UpdateCoverageAreaMute(self, value, qualifier):

        ca = int(qualifier['Coverage Area'])

        if 1 <= ca <= 8:
            CoverageAreaMuteCmdString = '< GET {:02d} CA_MUTE >'.format(ca)
            self.__UpdateHelper('CoverageAreaMute', CoverageAreaMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCoverageAreaMute')

    def __MatchCoverageAreaMute(self, match, tag):

        qualifier = {
            'Coverage Area': match.group(1).decode()
        }

        value = match.group(2).decode().title()
        self.WriteStatus('CoverageAreaMute', value, qualifier)

    def SetDeviceMute(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            DeviceMuteCmdString = '< SET DEVICE_AUDIO_MUTE {} >'.format(value.upper())
            self.__SetHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceMute')

    def UpdateDeviceMute(self, value, qualifier):

        DeviceMuteCmdString = '< GET DEVICE_AUDIO_MUTE >'
        self.__UpdateHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)

    def __MatchDeviceMute(self, match, tag):


        value = match.group(1).decode().title()
        self.WriteStatus('DeviceMute', value, None)

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

    def SetLEDBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            LEDBrightnessCmdString = '< SET LED_BRIGHTNESS {} >'.format(value // 20)
            self.__SetHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBrightness')

    def UpdateLEDBrightness(self, value, qualifier):

        LEDBrightnessCmdString = '< GET LED_BRIGHTNESS >'
        self.__UpdateHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)

    def __MatchLEDBrightness(self, match, tag):

        value = int(match.group(1).decode()) * 20
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

    def __MatchLEDPower(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LEDPower', value, None)

    def UpdateModelNumber(self, value, qualifier):

        ModelNumberCmdString = '< GET MODEL >'
        self.__UpdateHelper('ModelNumber', ModelNumberCmdString, value, qualifier)

    def __MatchModelNumber(self, match, tag):

        value = match.group(1).decode().strip()
        self.WriteStatus('ModelNumber', value, None)

    def UpdateOutputClipStatus(self, value, qualifier):
        
        OutputClipStatusCmdString = '< GET 0 AUDIO_OUT_CLIP_INDICATOR >'
        self.__UpdateHelper('OutputClipStatus', OutputClipStatusCmdString, value, qualifier)

    def __MatchOutputClipStatus(self, match, tag):

        ChannelStates = {
            '1'     : '1',
            '2'     : '2',
            '3'     : '3',
            '4'     : '4',
            '5'     : '5',
            '6'     : '6',
            '7'     : '7',
            '8'     : '8',
            '9'     : 'Automixer'
        }

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputClipStatus', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 10:
            PresetRecallCmdString = '< SET PRESET {:02d} >'.format(int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = '< GET PRESET >'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

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

    def SetReboot(self, value, qualifier):

        RebootCmdString = '< SET REBOOT >'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def UpdateTalkerPositionStatus(self, value, qualifier):

        TalkerPositionStatusCmdString = '< SET TALKER_POSITION_RATE 1000 >'
        self.__UpdateHelper('TalkerPositionStatus', TalkerPositionStatusCmdString, value, qualifier)

    def __MatchTalkerPositionStatus(self, match, tag):

        data = match.group(1).decode().strip().split()
        active_coverage_areas = set()

        if len(data) % 6 == 0:
            for offset in range(0, len(data), 6):
                coverage_area = int(data[offset + 1])
                if coverage_area != 0:
                    active_coverage_areas.add(coverage_area)

        if tag == 'Set':
            value = match.group(1).decode()
            self.WriteStatus('TalkerPositionStatus', '', None)
        else:
            value = ','.join(str(coverage_area) for coverage_area in sorted(active_coverage_areas))
            self.WriteStatus('TalkerPositionStatus', value, None)

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

        self.Error(['An error occurred.'])

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