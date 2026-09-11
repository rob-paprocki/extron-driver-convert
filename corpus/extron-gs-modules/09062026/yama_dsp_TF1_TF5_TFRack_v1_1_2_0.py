# Copyright 2025, Extron. All rights reserved.

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
            'TF1': self.yama_25_2973_32,
            'TF-Rack': self.yama_25_2973_32,
            'TF5': self.yama_25_2973_40
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AUXLevel': {'Parameters': ['Input Channel', 'AUX Channel'], 'Status': {}},
            'AUXMute': {'Parameters': ['Input Channel', 'AUX Channel'], 'Status': {}},
            'DCAMasterLevel': {'Parameters':['Channel'], 'Status': {}},
            'DCAMasterMute': {'Parameters':['Channel'], 'Status': {}},
            'FaderLevel': {'Parameters':['Channel'], 'Status': {}},
            'FaderMute': {'Parameters':['Channel'], 'Status': {}},
            'Firmware': { 'Status': {}},
            'InputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'MatrixLevel': {'Parameters':['Channel'], 'Status': {}},
            'MatrixMute': {'Parameters':['Channel'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'Preset': {'Parameters': ['Scene', 'Action'], 'Status': {}},
            'StereoAUXLevel': {'Parameters':['Input Channel','AUX Channel'], 'Status': {}},
            'StereoAUXMute': {'Parameters':['Input Channel','AUX Channel'], 'Status': {}},
            'StereoInLevel': {'Parameters': ['Channel'], 'Status': {}},
            'StereoInMute': {'Parameters': ['Channel'], 'Status': {}}
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/InCh/ToMix/Level ([0-9]{1,2}) ([0-9]{1,2}) (-?\d{1,5})[\s\S]*?\n'), self.__MatchAUXLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/InCh/ToMix/On ([0-9]{1,2}) ([0-9]{1,2}) ([01])[\s\S]*?\n'), self.__MatchAUXMute, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/DcaCh/Fader/Level ([0-7]) 0 (-?\d{1,5})[\s\S]*?\n'), self.__MatchDCAMasterLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/DcaCh/Fader/On ([0-7]) 0 ([01])[\s\S]*?\n'), self.__MatchDCAMasterMute, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/(Mono|St)/Fader/Level ([01]) 0 (-?\d{1,5})[\s\S]*?\n'), self.__MatchFaderLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/(Mono|St)/Fader/On ([01]) 0 ([01])[\s\S]*?\n'), self.__MatchFaderMute, None)
            self.AddMatchString(re.compile(b'OK devinfo version "?(V[.\d]+)"?\n'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/InCh/Fader/Level ([0-9]{1,2}) 0 (-?\d{1,5})[\s\S]*?\n'), self.__MatchInputLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/InCh/Fader/On ([0-9]{1,2}) 0 ([01])[\s\S]*?\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/Mtrx/Fader/Level ([0-3]) 0 (-?\d{1,5})[\s\S]*?\n'), self.__MatchMatrixLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/Mtrx/Fader/On ([0-3]) 0 ([01])[\s\S]*?\n'), self.__MatchMatrixMute, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/Mix/Fader/Level ([0-9]{1,2}) 0 (-?\d{1,5})[\s\S]*?\n'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/Mix/Fader/On ([0-9]{1,2}) 0 ([01])[\s\S]*?\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/StInCh/ToMix/Level ([0-3]) ([0-9]{1,2}) (-?\d{1,5})[\s\S]*?\n'), self.__MatchStereoAUXLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/StInCh/ToMix/On ([0-3]) ([0-9]{1,2}) ([01])[\s\S]*?\n'), self.__MatchStereoAUXMute, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY|OKm) (?:set|get) MIXER:Current/StInCh/Fader/Level ([0-3]) 0 (-?\d{1,5})[\s\S]*?\n'), self.__MatchStereoInLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|Notify|NOTIFY) (?:set|get) MIXER:Current/StInCh/Fader/On ([0-3]) 0 ([01])[\s\S]*?\n'), self.__MatchStereoInMute, None)

            self.AddMatchString(re.compile(b'(ERROR get InvalidArgument|ERROR unknown UnknownCommand)'), self.__MatchError, None)

    def SetAUXLevel(self, value, qualifier):

        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])

        if 1 <= input_channel <= self.MaxInputChannels and 1 <= aux_channel <= 20 and -138 <= value <= 10:
            AUXLevelCmdString = 'set MIXER:Current/InCh/ToMix/Level {0} {1} {2}\n'.format(input_channel - 1, aux_channel - 1, int(value*100))
            self.__SetHelper('AUXLevel', AUXLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAUXLevel')

    def UpdateAUXLevel(self, value, qualifier):

        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])

        if 1 <= input_channel <= self.MaxInputChannels and 1 <= aux_channel <= 20:
            AUXLevelCmdString = 'get MIXER:Current/InCh/ToMix/Level {0} {1}\n'.format(input_channel - 1, aux_channel - 1)
            self.__UpdateHelper('AUXLevel', AUXLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAUXLevel')

    def __MatchAUXLevel(self, match, tag):

        qualifier = {
            'Input Channel' : str(int(match.group(1).decode()) + 1),
            'AUX Channel'   : str(int(match.group(2).decode()) + 1)
        }

        value = int(match.group(3).decode()) / 100
        if -138 <= value <= 10:
            self.WriteStatus('AUXLevel', value, qualifier)

    def SetAUXMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])

        if 1 <= input_channel <= self.MaxInputChannels and 1 <= aux_channel <= 20 and value in ValueStateValues:
            AUXMuteCmdString = 'set MIXER:Current/InCh/ToMix/On {0} {1} {2}\n'.format(input_channel - 1, aux_channel - 1, ValueStateValues[value])
            self.__SetHelper('AUXMute', AUXMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAUXMute')

    def UpdateAUXMute(self, value, qualifier):

        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])

        if 1 <= input_channel <= self.MaxInputChannels and 1 <= aux_channel <= 20:
            AUXMuteCmdString = 'get MIXER:Current/InCh/ToMix/On {0} {1}\n'.format(input_channel - 1, aux_channel - 1)
            self.__UpdateHelper('AUXMute', AUXMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAUXMute')

    def __MatchAUXMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input Channel':    str(int(match.group(1).decode()) + 1),
            'AUX Channel':      str(int(match.group(2).decode()) + 1)
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('AUXMute', value, qualifier)

    def SetDCAMasterLevel(self, value, qualifier):

        channel_val = int(qualifier['Channel']) 
        if -138 <= value <= 10 and 1 <= channel_val <= 8:
            DCAMasterLevelCmdString = 'set MIXER:Current/DcaCh/Fader/Level {0} 0 {1}\n'.format(channel_val - 1, int(value*100))
            self.__SetHelper('DCAMasterLevel', DCAMasterLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAMasterLevel')

    def UpdateDCAMasterLevel(self, value, qualifier):

        channel_val = int(qualifier['Channel'])
        if 1 <= channel_val <= 8:
            DCAMasterLevelCmdString = 'get MIXER:Current/DcaCh/Fader/Level {0} 0\n'.format(channel_val - 1)
            self.__UpdateHelper('DCAMasterLevel', DCAMasterLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAMasterLevel')

    def __MatchDCAMasterLevel(self, match, tag):

        qualifier = {'Channel' : str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode()) / 100
        if -138 <= value <= 10:
            self.WriteStatus('DCAMasterLevel', value, qualifier)

    def SetDCAMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        channel_val = int(qualifier['Channel'])
        if 1 <= channel_val <= 8 and value in ValueStateValues:
            DCAMasterMuteCmdString = 'set MIXER:Current/DcaCh/Fader/On {0} 0 {1}\n'.format(channel_val - 1, ValueStateValues[value])
            self.__SetHelper('DCAMasterMute', DCAMasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAMasterMute')

    def UpdateDCAMasterMute(self, value, qualifier):

        channel_val = int(qualifier['Channel'])
        if 1 <= channel_val <= 8:
            DCAMasterMuteCmdString = 'get MIXER:Current/DcaCh/Fader/On {0} 0\n'.format(channel_val - 1)
            self.__UpdateHelper('DCAMasterMute', DCAMasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAMasterMute')

    def __MatchDCAMasterMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = str(int(match.group(1).decode()) + 1)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DCAMasterMute', value, qualifier)

    def SetFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Stereo L' : '0', 
            'Stereo R' : '1', 
        }

        channel_val = qualifier['Channel']
        if -138 <= value <= 10 and channel_val in ['Mono', 'Stereo L', 'Stereo R']:
            if 'Mono' in channel_val:
                FaderLevelCmdString = 'set MIXER:Current/Mono/Fader/Level 0 0 {0}\n'.format(int(value*100))
            else: 
                FaderLevelCmdString = 'set MIXER:Current/St/Fader/Level {0} 0 {1}\n'.format(ChannelStates[channel_val], int(value*100))

            self.__SetHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderLevel')

    def UpdateFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Stereo L' : '0', 
            'Stereo R' : '1', 
        }
        
        channel_val = qualifier['Channel']
        if 'Mono' in channel_val:
            FaderLevelCmdString = 'get MIXER:Current/Mono/Fader/Level 0 0\n'
            self.__UpdateHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        elif channel_val in ChannelStates:
            FaderLevelCmdString = 'get MIXER:Current/St/Fader/Level {0} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFaderLevel')

    def __MatchFaderLevel(self, match, tag):

        ChannelStates = {
            '0' : 'Stereo L', 
            '1' : 'Stereo R', 
        }

        value = int(match.group(3).decode()) / 100
        if -138 <= value <= 10:
            if match.group(1).decode() == 'Mono':
                self.WriteStatus('FaderLevel', value, {'Channel' : 'Mono'})
            else:
                self.WriteStatus('FaderLevel', value, {'Channel' : ChannelStates[match.group(2).decode()]})

    def SetFaderMute(self, value, qualifier):

        ChannelStates = {
            'Stereo L' : '0', 
            'Stereo R' : '1', 
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        channel_val = qualifier['Channel']
        if channel_val in ['Mono', 'Stereo L', 'Stereo R'] and value in ValueStateValues:
            if 'Mono' in channel_val:
                FaderMuteCmdString = 'set MIXER:Current/Mono/Fader/On 0 0 {0}\n'.format(ValueStateValues[value])
            else:
                FaderMuteCmdString = 'set MIXER:Current/St/Fader/On {0} 0 {1}\n'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('FaderMute', FaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderMute')

    def UpdateFaderMute(self, value, qualifier):

        ChannelStates = {
            'Stereo L' : '0', 
            'Stereo R' : '1', 
        }

        channel_val = qualifier['Channel']
        if 'Mono' in channel_val:
            FaderMuteCmdString = 'get MIXER:Current/Mono/Fader/On 0 0\n'
            self.__UpdateHelper('FaderMute', FaderMuteCmdString, value, qualifier)
        elif channel_val in ChannelStates:
            FaderMuteCmdString = 'get MIXER:Current/St/Fader/On {0} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FaderMute', FaderMuteCmdString, value, qualifier)

    def __MatchFaderMute(self, match, tag):

        ChannelStates = {
            '0' : 'Stereo L', 
            '1' : 'Stereo R', 
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(3).decode()]
        if match.group(1).decode() == 'Mono':
            self.WriteStatus('FaderMute', value, {'Channel' : 'Mono'})
        else:
            self.WriteStatus('FaderMute', value, {'Channel' : ChannelStates[match.group(2).decode()]})

    def UpdateFirmware(self, value, qualifier):


        FirmwareCmdString = 'devinfo version\n'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, None)

    def SetInputLevel(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= self.MaxInputChannels and -138 <= value <= 10:
            InputLevelCmdString = 'set MIXER:Current/InCh/Fader/Level {0} 0 {1}\n'.format(Channel - 1, int(value*100))
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= self.MaxInputChannels:
            InputLevelCmdString = 'get MIXER:Current/InCh/Fader/Level {0} 0\n'.format(Channel - 1)
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        qualifier = {'Channel': str(int(match.group(1).decode()) + 1)}

        value = int(match.group(2).decode()) / 100
        if -138 <= value <= 10:
            self.WriteStatus('InputLevel', value, qualifier)

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= self.MaxInputChannels and value in ValueStateValues:
            InputMuteCmdString = 'set MIXER:Current/InCh/Fader/On {0} 0 {1}\n'.format(Channel - 1, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= self.MaxInputChannels:
            InputMuteCmdString = 'get MIXER:Current/InCh/Fader/On {0} 0\n'.format(Channel - 1)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': str(int(match.group(1).decode()) + 1)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetMatrixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4 and -138 <= value <= 10:
            MatrixLevelCmdString = 'set MIXER:Current/Mtrx/Fader/Level {0} 0 {1}\n'.format(int(qualifier['Channel']) - 1, int(value*100))
            self.__SetHelper('MatrixLevel', MatrixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixLevel')

    def UpdateMatrixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4:
            MatrixLevelCmdString = 'get MIXER:Current/Mtrx/Fader/Level {0} 0\n'.format(int(qualifier['Channel']) - 1)
            self.__UpdateHelper('MatrixLevel', MatrixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixLevel')

    def __MatchMatrixLevel(self, match, tag):

        qualifier = {
            'Channel': str(int(match.group(1).decode()) + 1)
        }

        value = int(match.group(2).decode()) / 100
        if -138 <= value <= 10:
            self.WriteStatus('MatrixLevel', value, qualifier)

    def SetMatrixMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Channel']) <= 4 and value in ValueStateValues:
            MatrixMuteCmdString = 'set MIXER:Current/Mtrx/Fader/On {0} 0 {1}\n'.format(int(qualifier['Channel']) - 1, ValueStateValues[value])
            self.__SetHelper('MatrixMute', MatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMute')

    def UpdateMatrixMute(self, value, qualifier):


        if 1 <= int(qualifier['Channel']) <= 4:
            MatrixMuteCmdString = 'get MIXER:Current/Mtrx/Fader/On {0} 0\n'.format(int(qualifier['Channel']) - 1)
            self.__UpdateHelper('MatrixMute', MatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMute')

    def __MatchMatrixMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': str(int(match.group(1).decode()) + 1)
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MatrixMute', value, qualifier)

    def SetOutputLevel(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if -138 <= value <= 10 and 1 <= Channel <= 20:
            OutputLevelCmdString = 'set MIXER:Current/Mix/Fader/Level {0} 0 {1}\n'.format(Channel - 1, int(value*100))
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= 20:
            OutputLevelCmdString = 'get MIXER:Current/Mix/Fader/Level {0} 0\n'.format(Channel - 1)
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        qualifier = {
            'Channel': str(int(match.group(1).decode()) + 1)
        }

        value = int(match.group(2).decode()) / 100
        if -138 <= value <= 10:
            self.WriteStatus('OutputLevel', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= 20 and value in ValueStateValues:
            CmdString = 'set MIXER:Current/Mix/Fader/On {0} 0 {1}\n'.format(Channel - 1, ValueStateValues[value])
            self.__SetHelper('OutputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= 20:
            CmdString = 'get MIXER:Current/Mix/Fader/On {0} 0\n'.format(Channel - 1)
            self.__UpdateHelper('OutputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {
            'Channel': str(int(match.group(1).decode()) + 1)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPreset(self, value, qualifier):

        SceneStates = {
            'A': 'a',
            'B': 'b'
        }
        scene = qualifier['Scene']

        ActionStates = {
            'Recall':   'recall',
            'Store':    'update'
        }
        action = qualifier['Action']

        if action in ActionStates and scene in SceneStates and 0 <= int(value) <= 99:
            CmdString = 'ss{0}_ex scene_{1} {2}\n'.format(ActionStates[action], SceneStates[scene], value)
            self.__SetHelper('Preset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetStereoAUXLevel(self, value, qualifier):

        InputChannelStates = {
            '1 Left'  : '0',
            '1 Right' : '1',
            '2 Left'  : '2',
            '2 Right' : '3'
        }

        if qualifier['Input Channel'] in InputChannelStates and 1 <= int(qualifier['AUX Channel']) <= 20 and -138.0 <= value <= 10.0:
            inputChannel = InputChannelStates[qualifier['Input Channel']]
            auxChannel = int(qualifier['AUX Channel']) - 1
            StereoAUXLevelCmdString = 'set MIXER:Current/StInCh/ToMix/Level {0} {1} {2}\n'.format(inputChannel, auxChannel, int(value*100))
            self.__SetHelper('StereoAUXLevel', StereoAUXLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoAUXLevel')

    def UpdateStereoAUXLevel(self, value, qualifier):

        InputChannelStates = {
            '1 Left'  : '0',
            '1 Right' : '1',
            '2 Left'  : '2',
            '2 Right' : '3'
        }

        if qualifier['Input Channel'] in InputChannelStates and 1 <= int(qualifier['AUX Channel']) <= 20:
            inputChannel = int(InputChannelStates[qualifier['Input Channel']])
            auxChannel = int(qualifier['AUX Channel']) - 1
            StereoAUXLevelCmdString = 'get MIXER:Current/StInCh/ToMix/Level {0} {1}\n'.format(inputChannel, auxChannel)
            self.__UpdateHelper('StereoAUXLevel', StereoAUXLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStereoAUXLevel')

    def __MatchStereoAUXLevel(self, match, tag):

        InputChannelStates = {
            0 : '1 Left',
            1 : '1 Right',
            2 : '2 Left',
            3 : '2 Right'
        }

        qualifier = {
            'Input Channel' : InputChannelStates[int(match.group(1))],
            'AUX Channel'   : str(int(match.group(2).decode()) + 1)
        }

        value = int(match.group(3).decode()) / 100
        if -138.0 <= value <= 10.0:
            self.WriteStatus('StereoAUXLevel', value, qualifier)

    def SetStereoAUXMute(self, value, qualifier):

        InputChannelStates = {
            '1 Left'    : '0',
            '1 Right'   : '1',
            '2 Left'    : '2',
            '2 Right'   : '3'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if qualifier['Input Channel'] in InputChannelStates and 1 <= int(qualifier['AUX Channel']) <= 20 and value in ValueStateValues:
            inputChannel = InputChannelStates[qualifier['Input Channel']]
            auxChannel = int(qualifier['AUX Channel']) - 1
            StereoAUXMuteCmdString = 'set MIXER:Current/StInCh/ToMix/On {0} {1} {2}\n'.format(inputChannel, auxChannel, ValueStateValues[value])
            self.__SetHelper('StereoAUXMute', StereoAUXMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoAUXMute')

    def UpdateStereoAUXMute(self, value, qualifier):

        InputChannelStates = {
            '1 Left'    : '0',
            '1 Right'   : '1',
            '2 Left'    : '2',
            '2 Right'   : '3'
        }

        if qualifier['Input Channel'] in InputChannelStates and 1 <= int(qualifier['AUX Channel']) <= 20:
            inputChannel = InputChannelStates[qualifier['Input Channel']]
            auxChannel = int(qualifier['AUX Channel']) - 1
            StereoAUXMuteCmdString = 'get MIXER:Current/StInCh/ToMix/On {0} {1}\n'.format(inputChannel, auxChannel)
            self.__UpdateHelper('StereoAUXMute', StereoAUXMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStereoAUXMute')

    def __MatchStereoAUXMute(self, match, tag):

        InputChannelStates = {
            '0' : '1 Left',
            '1' : '1 Right',
            '2' : '2 Left',
            '3' : '2 Right'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {
            'Input Channel' : InputChannelStates[match.group(1).decode()],
            'AUX Channel'   : str(int(match.group(2).decode()) + 1)
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('StereoAUXMute', value, qualifier)

    def SetStereoInLevel(self, value, qualifier):

        ChannelStates = {
            '1L': '0',
            '1R': '1',
            '2L': '2',
            '2R': '3'
        }

        channel = qualifier['Channel']
        if channel in ChannelStates and -138 <= value <= 10:
            StereoInLevelCmdString = 'set MIXER:Current/StInCh/Fader/Level {0} 0 {1} 0\n'.format(ChannelStates[channel], int(value*100))
            self.__SetHelper('StereoInLevel', StereoInLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoInLevel')

    def UpdateStereoInLevel(self, value, qualifier):

        ChannelStates = {
            '1L': '0',
            '1R': '1',
            '2L': '2',
            '2R': '3'
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            StereoInLevelCmdString = 'get MIXER:Current/StInCh/Fader/Level {0} 0\n'.format(ChannelStates[channel])
            self.__UpdateHelper('StereoInLevel', StereoInLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStereoInLevel')

    def __MatchStereoInLevel(self, match, tag):

        ChannelStates = {
            '0': '1L',
            '1': '1R',
            '2': '2L',
            '3': '2R'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = int(match.group(2).decode()) / 100
        if -138 <= value <= 10:
            self.WriteStatus('StereoInLevel', value, qualifier)

    def SetStereoInMute(self, value, qualifier):

        ChannelStates = {
            '1L': '0',
            '1R': '1',
            '2L': '2',
            '2R': '3'
        }
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if channel in ChannelStates and value in ValueStateValues:
            StereoInMuteCmdString = 'set MIXER:Current/StInCh/Fader/On {0} 0 {1}\n'.format(ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('StereoInMute', StereoInMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoInMute')

    def UpdateStereoInMute(self, value, qualifier):

        ChannelStates = {
            '1L': '0',
            '1R': '1',
            '2L': '2',
            '2R': '3'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            StereoInMuteCmdString = 'get MIXER:Current/StInCh/Fader/On {0} 0\n'.format(ChannelStates[channel])
            self.__UpdateHelper('StereoInMute', StereoInMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStereoInMute')

    def __MatchStereoInMute(self, match, tag):

        ChannelStates = {
            '0': '1L',
            '1': '1R',
            '2': '2L',
            '3': '2R'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('StereoInMute', value, qualifier)

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

        self.Error(['An error occurred: {}'.format(match.group(0).decode())])
   
    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def yama_25_2973_40(self):

        self.MaxInputChannels = 40

    def yama_25_2973_32(self):

        self.MaxInputChannels = 32

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