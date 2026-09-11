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
            'MXA710-2FT': self.shur_31_4923_2ft,
            'MXA710-4FT': self.shur_31_4923_4ft
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
            'IdentifyMicrophone': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'LEDMutedColor': { 'Status': {}},
            'LEDMutedState': { 'Status': {}},
            'LEDUnmutedColor': { 'Status': {}},
            'LEDUnmutedState': { 'Status': {}},
            'LEDPower': { 'Status': {}},
            'LobeBeamAngle': {'Parameters':['Channel'], 'Status': {}},
            'LobeBeamWidth': {'Parameters':['Channel'], 'Status': {}},
            'ModelNumber': { 'Status': {}},
            'OutputClipStatus': {'Parameters':['Channel'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Reboot': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP NUM_ACTIVE_MICS ([1-8]) >'), self.__MatchActiveMicChannels, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) AUDIO_GAIN_HI_RES (\d{1,4}) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) AUDIO_GAIN_POSTGATE (\d{1,4}) >'), self.__MatchAudioGainPostgate, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) AUDIO_IN_PEAK_LVL (\d{3}) >'), self.__MatchAudioPeakLevelStatus, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) AUDIO_IN_RMS_LVL (\d{3}) >'), self.__MatchAudioRMSLevelStatus, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) AUTOMIX_GATE_OUT_EXT_SIG (ON|OFF) >'), self.__MatchAutomixerGateOutStatus, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) AUDIO_MUTE (ON|OFF) >'), self.__MatchChannelMute, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_AUDIO_MUTE (ON|OFF) >'), self.__MatchDeviceMute, None)
            self.AddMatchString(re.compile(b'< REP FLASH (ON|OFF) >'), self.__MatchIdentifyMicrophone, None)
            self.AddMatchString(re.compile(b'< REP LED_BRIGHTNESS ([0-5]) >'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'< REP DEV_LED_IN_STATE (ON|OFF) >'), self.__MatchLEDPower, None)
            self.AddMatchString(re.compile(b'< REP LED_COLOR_MUTED (RED|ORANGE|GOLD|YELLOW|YELLOWGREEN|GREEN|TURQUOISE|POWDERBLUE|CYAN|SKYBLUE|BLUE|PURPLE|LIGHTPURPLE|VIOLET|ORCHID|PINK|WHITE) >', re.I), self.__MatchLEDMutedColor, None)
            self.AddMatchString(re.compile(b'< REP LED_COLOR_UNMUTED (RED|ORANGE|GOLD|YELLOW|YELLOWGREEN|GREEN|TURQUOISE|POWDERBLUE|CYAN|SKYBLUE|BLUE|PURPLE|LIGHTPURPLE|VIOLET|ORCHID|PINK|WHITE) >', re.I), self.__MatchLEDUnmutedColor, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_MUTED (ON|FLASHING|OFF) >', re.I), self.__MatchLEDMutedState, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_UNMUTED (ON|FLASHING|OFF) >', re.I), self.__MatchLEDUnmutedState, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) BEAM_ANGLE (-?\d{1,2}) >'), self.__MatchLobeBeamAngle, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) BEAM_W (NARROW|MEDIUM|WIDE) >'), self.__MatchLobeBeamWidth, None)
            self.AddMatchString(re.compile(b'< REP MODEL (.+?) >'), self.__MatchModelNumber, None)
            self.AddMatchString(re.compile(b'< REP 0?(\d) AUDIO_OUT_CLIP_INDICATOR (ON|OFF) >'), self.__MatchOutputClipStatus, None)
            self.AddMatchString(re.compile(b'< REP PRESET ([01]\d) >'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)
    
    def UpdateActiveMicChannels(self, value, qualifier):

        ActiveMicChannelsCmdString = '< GET NUM_ACTIVE_MICS >'
        self.__UpdateHelper('ActiveMicChannels', ActiveMicChannelsCmdString, value, qualifier)

    def __MatchActiveMicChannels(self, match, tag):

        value = self.ChannelStates[match.group(1).decode()]
        self.WriteStatus('ActiveMicChannels', value, None)

    def SetAudioGain(self, value, qualifier):

        temp = round(value, 1)
        if -110 <= temp <= 30 and qualifier['Channel'] in self.setChannel:
            scaledValue = int(temp * 10) + 1100
            AudioGainCmdString = '< SET {0} AUDIO_GAIN_HI_RES {1} >'.format(self.setChannel[qualifier['Channel']], scaledValue)
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        if qualifier['Channel'] in self.setChannel:
            AudioGainCmdString = '< GET {} AUDIO_GAIN_HI_RES >'.format(self.setChannel[qualifier['Channel']])
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        qualifier = {'Channel' : self.matchChannel[match.group(1).decode()]}
        value = (int(match.group(2)) - 1100) / 10
        if -110 <= value <= 30:
            self.WriteStatus('AudioGain', value, qualifier)

    def SetAudioGainPostgate(self, value, qualifier):

        temp = round(value, 1)
        if -110 <= temp <= 30 and qualifier['Channel'] in self.setChannel:
            scaledValue = int(temp * 10) + 1100
            AudioGainPostgateCmdString = '< SET {0} AUDIO_GAIN_POSTGATE {1} >'.format(self.setChannel[qualifier['Channel']], scaledValue)
            self.__SetHelper('AudioGainPostgate', AudioGainPostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainPostgate')

    def UpdateAudioGainPostgate(self, value, qualifier):

        if qualifier['Channel'] in self.setChannel:
            AudioGainPostgateCmdString = '< GET {} AUDIO_GAIN_POSTGATE >'.format(self.setChannel[qualifier['Channel']])
            self.__UpdateHelper('AudioGainPostgate', AudioGainPostgateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGainPostgate')

    def __MatchAudioGainPostgate(self, match, tag):

        qualifier = {'Channel': self.matchChannel[match.group(1).decode()]}
        value = (int(match.group(2)) - 1100) / 10
        if -110 <= value <= 30:
            self.WriteStatus('AudioGainPostgate', value, qualifier)

    def UpdateAudioPeakLevelStatus(self, value, qualifier):

        AudioPeakLevelStatusCmdString = '< GET 0 AUDIO_IN_PEAK_LVL >'
        self.__UpdateHelper('AudioPeakLevelStatus', AudioPeakLevelStatusCmdString, value, qualifier)

    def __MatchAudioPeakLevelStatus(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = self.matchChannel[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('AudioPeakLevelStatus', value, qualifier)

    def UpdateAudioRMSLevelStatus(self, value, qualifier):

        AudioLevelCmdString = '< GET 0 AUDIO_IN_RMS_LVL >'
        self.__UpdateHelper('AudioRMSLevelStatus', AudioLevelCmdString, value, qualifier)

    def __MatchAudioRMSLevelStatus(self, match, tag):

        qualifier = {'Channel' : self.matchChannel[match.group(1).decode()]}
        value = int(match.group(2).decode())
        self.WriteStatus('AudioRMSLevelStatus', value, qualifier)

    def UpdateAutomixerGateOutStatus(self, value, qualifier):

        if qualifier['Channel'] in self.setChannel:
            AutomixerGateOutStatusCmdString = '< GET {} AUTOMIX_GATE_OUT_EXT_SIG >'.format(self.setChannel[qualifier['Channel']])
            self.__UpdateHelper('AutomixerGateOutStatus', AutomixerGateOutStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerGateOutStatus')

    def __MatchAutomixerGateOutStatus(self, match, tag):

        qualifier = {'Channel': self.matchChannel[match.group(1).decode()]}
        value = match.group(2).decode().title()
        self.WriteStatus('AutomixerGateOutStatus', value, qualifier)

    def SetChannelMute(self, value, qualifier):

        if value in ['On', 'Off', 'Toggle'] and qualifier['Channel'] in self.setChannel:
            ChannelMuteCmdString = '< SET 0{0} AUDIO_MUTE {1} >'.format(self.setChannel[qualifier['Channel']], value.upper())
            self.__SetHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMute')

    def UpdateChannelMute(self, value, qualifier):

        if qualifier['Channel'] in self.setChannel:
            ChannelMuteCmdString = '< GET 0{} AUDIO_MUTE >'.format(self.setChannel[qualifier['Channel']])
            self.__UpdateHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelMute')

    def __MatchChannelMute(self, match, tag):

        qualifier = {'Channel' : self.matchChannel[match.group(1).decode()]}
        value = match.group(2).decode().title()
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
            'On'     : '< SET DEVICE_AUDIO_MUTE ON >',
            'Off'    : '< SET DEVICE_AUDIO_MUTE OFF >',
            'Toggle' : '< SET DEVICE_AUDIO_MUTE TOGGLE >'
        }

        if value in ValueStateValues:
            DeviceMuteCmdString = ValueStateValues[value]
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
            'On'  : '< SET FLASH ON >',
            'Off' : '< SET FLASH OFF >'
        }

        if value in ValueStateValues:
            FlashCmdString = ValueStateValues[value]
            self.__SetHelper('IdentifyMicrophone', FlashCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIdentifyMicrophone')

    def UpdateIdentifyMicrophone(self, value, qualifier):

        FlashCmdString = '< GET FLASH >'
        self.__UpdateHelper('IdentifyMicrophone', FlashCmdString, value, qualifier)

    def __MatchIdentifyMicrophone(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('IdentifyMicrophone', value, None)

    def SetLEDBrightness(self, value, qualifier):

        ValueStateValues = {
            'Disabled'  : '< SET LED_BRIGHTNESS 0 >',
            '20%'       : '< SET LED_BRIGHTNESS 1 >',
            '40%'       : '< SET LED_BRIGHTNESS 2 >',
            '60%'       : '< SET LED_BRIGHTNESS 3 >',
            '80%'       : '< SET LED_BRIGHTNESS 4 >',
            '100%'      : '< SET LED_BRIGHTNESS 5 >'
        }

        if value in ValueStateValues:
            LEDBrightnessCmdString = ValueStateValues[value]
            self.__SetHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBrightness')

    def UpdateLEDBrightness(self, value, qualifier):

        LEDBrightnessCmdString = '< GET LED_BRIGHTNESS >'
        self.__UpdateHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)

    def __MatchLEDBrightness(self, match, tag):

        ValueStateValues = {
            '0' : 'Disabled', 
            '1' : '20%', 
            '2' : '40%', 
            '3' : '60%', 
            '4' : '80%', 
            '5' : '100%'
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

    def SetLobeBeamAngle(self, value, qualifier):

        if -90 <= value <= 90 and qualifier['Channel'] in self.setChannel:
            LobeBeamAngleCmdString = '< SET {0} BEAM_ANGLE {1} >'.format(self.setChannel[qualifier['Channel']], value)
            self.__SetHelper('LobeBeamAngle', LobeBeamAngleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLobeBeamAngle')

    def UpdateLobeBeamAngle(self, value, qualifier):

        if qualifier['Channel'] in self.setChannel:
            LobeBeamAngleCmdString = '< GET {} BEAM_ANGLE >'.format(self.setChannel[qualifier['Channel']])
            self.__UpdateHelper('LobeBeamAngle', LobeBeamAngleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLobeBeamAngle')

    def __MatchLobeBeamAngle(self, match, tag):

        qualifier = {'Channel': self.matchChannel[match.group(1).decode()]}
        value = int(match.group(2).decode())
        if -90 <= value <= 90:
            self.WriteStatus('LobeBeamAngle', value, qualifier)

    def SetLobeBeamWidth(self, value, qualifier):

        ValueStateValues = {
            'Wide'   : 'WIDE',
            'Medium' : 'MEDIUM',
            'Narrow' : 'NARROW'
        }

        if value in ValueStateValues and qualifier['Channel'] in self.setChannel:
            LobeBeamWidthCmdString = '< SET {0} BEAM_W {1} >'.format(self.setChannel[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('LobeBeamWidth', LobeBeamWidthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLobeBeamWidth')

    def UpdateLobeBeamWidth(self, value, qualifier):

        if qualifier['Channel'] in self.setChannel:
            LobeBeamWidthCmdString = '< GET {} BEAM_W >'.format(self.setChannel[qualifier['Channel']])
            self.__UpdateHelper('LobeBeamWidth', LobeBeamWidthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLobeBeamWidth')

    def __MatchLobeBeamWidth(self, match, tag):

        qualifier = {'Channel': self.matchChannel[match.group(1).decode()]}
        value = match.group(2).decode().title()
        self.WriteStatus('LobeBeamWidth', value, qualifier)

    def UpdateModelNumber(self, value, qualifier):

        ModelNumberCmdString = '< GET MODEL >'
        self.__UpdateHelper('ModelNumber', ModelNumberCmdString, value, qualifier)

    def __MatchModelNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ModelNumber', value, None)

    def UpdateOutputClipStatus(self, value, qualifier):

        OutputClipStatusCmdString = '< GET 0 AUDIO_OUT_CLIP_INDICATOR >'
        self.__UpdateHelper('OutputClipStatus', OutputClipStatusCmdString, value, qualifier)

    def __MatchOutputClipStatus(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = self.matchChannel[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputClipStatus', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 10:
            PresetsCmdString = '< SET PRESET {:02d} >'.format(int(value))
            self.__SetHelper('PresetRecall', PresetsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = '< GET PRESET >'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        value = int(match.group(1))
        if 1 <= value <= 10:
            self.WriteStatus('PresetRecall', str(value), None)

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

        self.Error(['An error occurred.'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def shur_31_4923_2ft(self):

        self.setChannel = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            'Automixer' : '5'
        }

        self.matchChannel = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : 'Automixer'
        }

        self.ChannelStates = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4'
        }

    def shur_31_4923_4ft(self):

        self.setChannel = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8',
            'Automixer' : '9'
        }

        self.matchChannel = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8',
            '9' : 'Automixer'
        }

        self.ChannelStates = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8'
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