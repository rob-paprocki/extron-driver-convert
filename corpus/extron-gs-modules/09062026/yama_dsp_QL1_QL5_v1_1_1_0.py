from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
            'QL5': self.yama_25_2882_QL5,
            'QL1': self.yama_25_2882_QL1,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DCAGroupLevel': {'Parameters':['Channel'], 'Status': {}},
            'DCAGroupMute': {'Parameters':['Channel'], 'Status': {}},
            'DeviceStatus': {'Status': {}},
            'InputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'MatrixLevel': {'Parameters': ['Channel'], 'Status': {}},
            'MatrixMute': {'Parameters': ['Channel'], 'Status': {}},
            'MixLevel': {'Parameters': ['Channel'], 'Status': {}},
            'MixMute': {'Parameters': ['Channel'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'StereoLevel': {'Parameters': ['Channel'], 'Status': {}},
            'StereoMute': {'Parameters': ['Channel'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'MIXER:Current/DCA/Fader/Level ([0-9]{1,2}) 0 (-?[0-9]{1,5})'), self.__MatchDCAGroupLevel, None)
            self.AddMatchString(re.compile(b'MIXER:Current/DCA/Fader/On ([0-9]{1,2}) 0 ([01])'), self.__MatchDCAGroupMute, None)
            self.AddMatchString(re.compile(b'OK devstatus runmode "(normal|emergency|booting|update|diagnostics)"'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'MIXER:Current/InCh/Fader/Level ([0-9]{1,2}) 0 (-?[0-9]{1,5})'), self.__MatchInputLevel, None)
            self.AddMatchString(re.compile(b'MIXER:Current/InCh/Fader/On ([0-9]{1,2}) 0 ([01])'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'MIXER:Current/Mtrx/Fader/Level ([0-7]) 0 (-?[0-9]{1,5})'), self.__MatchMatrixLevel, None)
            self.AddMatchString(re.compile(b'MIXER:Current/Mtrx/Fader/On ([0-7]) 0 ([01])'), self.__MatchMatrixMute, None)
            self.AddMatchString(re.compile(b'MIXER:Current/Mix/Fader/Level ([0-9]{1,2}) 0 (-?[0-9]{1,5})'), self.__MatchMixLevel, None)
            self.AddMatchString(re.compile(b'MIXER:Current/Mix/Fader/On ([0-9]{1,2}) 0 ([01])'), self.__MatchMixMute, None)
            self.AddMatchString(re.compile(b'sscurrent_ex MIXER:Lib/Scene ([0-9]{1,3})'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'MIXER:Current/St/Fader/Level ([0-2]) 0 (-?[0-9]{1,5})'), self.__MatchStereoLevel, None)
            self.AddMatchString(re.compile(b'MIXER:Current/St/Fader/On ([0-2]) 0 ([01])'), self.__MatchStereoMute, None)
            self.AddMatchString(re.compile(b'ERROR(.*)\n'), self.__MatchError, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'devstatus runmode\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'normal': 'Normal',
            'emergency': 'Emergency',
            'booting': 'Booting',
            'update': 'Update',
            'diagnostics': 'Diagnostics'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    # Begin DCAGroupLevel
    ################################################################################################################################
    # Page 9, (EN)SCP_Control_ParameterList_CL_QL_r1.0.1.pdf
    def SetDCAGroupLevel(self, value, qualifier):
        channel = int(qualifier['Channel'])
        oldValue = self.ReadStatus('DCAGroupLevel', qualifier)
        if -138 <= value <= 10 and 1 <= channel <= 16:
            # In the case that status is not configured, let the command send out what ever control is configured
            if oldValue:
                # Account for different step sizes
                # Step Size 3
                if oldValue != value:
                    if -138 < value <= -96:
                        if -3 < (oldValue - value) < 3:
                            if oldValue < value:
                                value = round(value) + 3
                            else:
                                value = round(value) - 3
                    # Step Size 1
                    elif -96 < value <= -78:
                        if -1 < (oldValue - value) < 1:
                            if oldValue < value:
                                value = round(value) + 1
                            else:
                                value = round(value) - 1
                    # Step Size 0.2
                    elif -78 < value <= -40:
                        if -0.2 < (oldValue - value) < 0.2:
                            if oldValue < value:
                                value = round(value + .15, 2)
                            else:
                                value = round(value - .15, 2)
                    # Step Size 0.1
                    elif -40 < value <= -20:
                        if -0.1 < (oldValue - value) < 0.1:
                            if oldValue < value:
                                value = round(value + .05, 2)
                            else:
                                value = round(value - .05, 2)
                    # Step size .05, do nothing
                    
            DCAGroupLevelCmdString = 'set MIXER:Current/DCA/Fader/Level {0} 0 {1}\n'.format(channel - 1, int(value * 100))
            self.__SetHelper('DCAGroupLevel', DCAGroupLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set DCAGroupLevel')

    def UpdateDCAGroupLevel(self, value, qualifier):
        channel = int(qualifier['Channel'])
        if 1 <= channel <= 16:
            DCAGroupLevelCmdString = 'get MIXER:Current/DCA/Fader/Level {0} 0\n'.format(channel - 1)
            self.__UpdateHelper('DCAGroupLevel', DCAGroupLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Update DCAGroupLevel')

    def __MatchDCAGroupLevel(self, match, tag):
        qualifier = {'Channel' : str(int(match.group(1)) + 1)}
        value = int(match.group(2).decode()) / 100
        if value < -138:
            value = -138
        self.WriteStatus('DCAGroupLevel', value, qualifier)

    def SetDCAGroupMute(self, value, qualifier):
        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 16:
            DCAGroupMuteCmdString = 'set MIXER:Current/DCA/Fader/On {0} 0 {1}\n'.format(channel - 1, ValueStateValues[value])
            self.__SetHelper('DCAGroupMute', DCAGroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set DCAGroupMute')

    def UpdateDCAGroupMute(self, value, qualifier):
        channel = int(qualifier['Channel'])
        if 1 <= channel <= 16:
            DCAGroupMuteCmdString = 'get MIXER:Current/DCA/Fader/On {0} 0\x0A'.format(channel - 1)
            self.__UpdateHelper('DCAGroupMute', DCAGroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Update DCAGroupMute')

    def __MatchDCAGroupMute(self, match, tag):
        """DCA Group Mute MatchString Handler

        """
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {'Channel' : str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DCAGroupMute', value, qualifier)

    def SetInputLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        oldValue = self.ReadStatus('InputLevel', qualifier)
        if -138 <= value <= 10 and 1 <= channel <= self.InputSize:
            if oldValue:
                if oldValue != value:
                    if -138 < value <= -96:
                        if -3 < (oldValue - value) < 3:
                            if oldValue < value:
                                value = round(value) + 3
                            else:
                                value = round(value) - 3
                    elif -96 < value <= -78:
                        if -1 < (oldValue - value) < 1:
                            if oldValue < value:
                                value = round(value) + 1
                            else:
                                value = round(value) - 1
                    elif -78 < value <= -40:
                        if -0.2 < (oldValue - value) < 0.2:
                            if oldValue < value:
                                value = round(value + .15, 2)
                            else:
                                value = round(value - .15, 2)
                    elif -40 < value <= -20:
                        if -0.1 < (oldValue - value) < 0.1:
                            if oldValue < value:
                                value = round(value + .05, 2)
                            else:
                                value = round(value - .05, 2)

            InputLevelCmdString = 'set MIXER:Current/InCh/Fader/Level {0} 0 {1}\n'.format(channel - 1, int(value * 100))
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)  # Query delay not needed, tested with the device
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            InputLevelCmdString = 'get MIXER:Current/InCh/Fader/Level {0} 0\n'.format(channel - 1)
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        qualifier = {'Channel': str(int(match.group(1)) + 1)}
        value = int(match.group(2).decode()) / 100
        if value < -138:
            value = -138
        self.WriteStatus('InputLevel', value, qualifier)

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            InputMuteCmdString = 'set MIXER:Current/InCh/Fader/On {0} 0 {1}\n'.format(channel - 1, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            InputMuteCmdString = 'get MIXER:Current/InCh/Fader/On {0} 0\n'.format(channel - 1)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel': str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetMatrixLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        oldValue = self.ReadStatus('MatrixLevel', qualifier)
        if -138 <= value <= 10 and 1 <= channel <= 8:
            if oldValue:
                if oldValue != value:
                    if -138 < value <= -96:
                        if -3 < (oldValue - value) < 3:
                            if oldValue < value:
                                value = round(value) + 3
                            else:
                                value = round(value) - 3
                    elif -96 < value <= -78:
                        if -1 < (oldValue - value) < 1:
                            if oldValue < value:
                                value = round(value) + 1
                            else:
                                value = round(value) - 1
                    elif -78 < value <= -40:
                        if -0.2 < (oldValue - value) < 0.2:
                            if oldValue < value:
                                value = round(value + .15, 2)
                            else:
                                value = round(value - .15, 2)
                    elif -40 < value <= -20:
                        if -0.1 < (oldValue - value) < 0.1:
                            if oldValue < value:
                                value = round(value + .05, 2)
                            else:
                                value = round(value - .05, 2)

            MatrixLevelCmdString = 'set MIXER:Current/Mtrx/Fader/Level {0} 0 {1}\n'.format(channel - 1, int(value * 100))
            self.__SetHelper('MatrixLevel', MatrixLevelCmdString, value, qualifier)  # Query delay not needed, tested on the device
        else:
            self.Discard('Invalid Command for SetMatrixLevel')

    def UpdateMatrixLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 8:
            MatrixLevelCmdString = 'get MIXER:Current/Mtrx/Fader/Level {0} 0\n'.format(channel - 1)
            self.__UpdateHelper('MatrixLevel', MatrixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixLevel')

    def __MatchMatrixLevel(self, match, tag):

        qualifier = {'Channel': str(int(match.group(1)) + 1)}
        value = int(match.group(2).decode()) / 100
        if value < -138:
            value = -138
        self.WriteStatus('MatrixLevel', value, qualifier)

    def SetMatrixMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 8:
            MatrixMuteCmdString = 'set MIXER:Current/Mtrx/Fader/On {0} 0 {1}\n'.format(channel - 1, ValueStateValues[value])
            self.__SetHelper('MatrixMute', MatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMute')

    def UpdateMatrixMute(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 8:
            MatrixMuteCmdString = 'get MIXER:Current/Mtrx/Fader/On {0} 0\n'.format(channel - 1)
            self.__UpdateHelper('MatrixMute', MatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMute')

    def __MatchMatrixMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel': str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MatrixMute', value, qualifier)

    def SetMixLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        oldValue = self.ReadStatus('MixLevel', qualifier)
        if -138 <= value <= 10 and 1 <= channel <= 16:
            if oldValue:
                if oldValue != value:
                    if -138 < value <= -96:
                        if -3 < (oldValue - value) < 3:
                            if oldValue < value:
                                value = round(value) + 3
                            else:
                                value = round(value) - 3
                    elif -96 < value <= -78:
                        if -1 < (oldValue - value) < 1:
                            if oldValue < value:
                                value = round(value) + 1
                            else:
                                value = round(value) - 1
                    elif -78 < value <= -40:
                        if -0.2 < (oldValue - value) < 0.2:
                            if oldValue < value:
                                value = round(value + .15, 2)
                            else:
                                value = round(value - .15, 2)
                    elif -40 < value <= -20:
                        if -0.1 < (oldValue - value) < 0.1:
                            if oldValue < value:
                                value = round(value + .05, 2)
                            else:
                                value = round(value - .05, 2)

            MixLevelCmdString = 'set MIXER:Current/Mix/Fader/Level {0} 0 {1}\n'.format(channel - 1, int(value * 100))
            self.__SetHelper('MixLevel', MixLevelCmdString, value, qualifier)  # Query delay not needed, tested on the device
        else:
            self.Discard('Invalid Command for SetMixLevel')

    def UpdateMixLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 16:
            MixLevelCmdString = 'get MIXER:Current/Mix/Fader/Level {0} 0\n'.format(channel - 1)
            self.__UpdateHelper('MixLevel', MixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixLevel')

    def __MatchMixLevel(self, match, tag):

        qualifier = {'Channel': str(int(match.group(1)) + 1)}
        value = int(match.group(2).decode()) / 100
        if value < -138:
            value = -138
        self.WriteStatus('MixLevel', value, qualifier)

    def SetMixMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        channel = int(qualifier['Channel'])
        if 1 <= channel <= 16:
            MixMuteCmdString = 'set MIXER:Current/Mix/Fader/On {0} 0 {1}\n'.format(channel - 1, ValueStateValues[value])
            self.__SetHelper('MixMute', MixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixMute')

    def UpdateMixMute(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 16:
            MixMuteCmdString = 'get MIXER:Current/Mix/Fader/On {0} 0\x0A'.format(channel - 1)
            self.__UpdateHelper('MixMute', MixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixMute')

    def __MatchMixMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel': str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MixMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 300:
            PresetRecallCmdString = 'ssrecall_ex MIXER:Lib/Scene {0}\n'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)  # Query delay not needed, tested with the device
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'sscurrent_ex MIXER:Lib/Scene\n'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PresetRecall', value, None)

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 300:
            PresetSaveCmdString = 'ssupdate_ex MIXER:Lib/Scene {0}\n'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetStereoLevel(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
            'Mono(C)': '2'
        }

        channel = qualifier['Channel']
        oldValue = self.ReadStatus('StereoLevel', qualifier)
        if -138 <= value <= 10 and channel in ChannelStates:
            if oldValue:
                if oldValue != value:
                    if -138 < value <= -96:
                        if -3 < (oldValue - value) < 3:
                            if oldValue < value:
                                value = round(value) + 3
                            else:
                                value = round(value) - 3
                    elif -96 < value <= -78:
                        if -1 < (oldValue - value) < 1:
                            if oldValue < value:
                                value = round(value) + 1
                            else:
                                value = round(value) - 1
                    elif -78 < value <= -40:
                        if -0.2 < (oldValue - value) < 0.2:
                            if oldValue < value:
                                value = round(value + .15, 2)
                            else:
                                value = round(value - .15, 2)
                    elif -40 < value <= -20:
                        if -0.1 < (oldValue - value) < 0.1:
                            if oldValue < value:
                                value = round(value + .05, 2)
                            else:
                                value = round(value - .05, 2)

            StereoLevelCmdString = 'set MIXER:Current/St/Fader/Level {0} 0 {1}\n'.format(ChannelStates[channel], int(value * 100))
            self.__SetHelper('StereoLevel', StereoLevelCmdString, value, qualifier)  # Query delay not needed, tested on the device
        else:
            self.Discard('Invalid Command for SetStereoLevel')

    def UpdateStereoLevel(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
            'Mono(C)': '2'
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            StereoLevelCmdString = 'get MIXER:Current/St/Fader/Level {0} 0\n'.format(ChannelStates[channel])
            self.__UpdateHelper('StereoLevel', StereoLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStereoLevel')

    def __MatchStereoLevel(self, match, tag):

        ChannelStates = {
            '0': 'Stereo L',
            '1': 'Stereo R',
            '2': 'Mono(C)'
        }

        qualifier = {'Channel': ChannelStates[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 100
        if value < -138:
            value = -138
        self.WriteStatus('StereoLevel', value, qualifier)

    def SetStereoMute(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
            'Mono(C)': '2'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            StereoMuteCmdString = 'set MIXER:Current/St/Fader/On {0} 0 {1}\n'.format(ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('StereoMute', StereoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoMute')

    def UpdateStereoMute(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
            'Mono(C)': '2'
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            StereoMuteCmdString = 'get MIXER:Current/St/Fader/On {0} 0\n'.format(ChannelStates[channel])
            self.__UpdateHelper('StereoMute', StereoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStereoMute')

    def __MatchStereoMute(self, match, tag):

        ChannelStates = {
            '0': 'Stereo L',
            '1': 'Stereo R',
            '2': 'Mono(C)'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel': ChannelStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('StereoMute', value, qualifier)

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

    def yama_25_2882_QL5(self):
        self.InputSize = 64

    def yama_25_2882_QL1(self):
        self.InputSize = 32
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
