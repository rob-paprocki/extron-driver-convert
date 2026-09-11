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
            'AnalogInputGainSwitch': { 'Status': {}},
            'AnalogOutputGainSwitch': { 'Status': {}},
            'AudioGain': {'Parameters': ['Channel'], 'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'CallStatus': { 'Status': {}},
            'DeviceAudioMute': { 'Status': {}},
            'LogicMute': { 'Status': {}},
            'MatrixMixerGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixMixerRouting': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'Preset': { 'Status': {}}
        }

        self.call_status_enabled = False
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP 05 AUDIO_IN_LVL_SWITCH (LINE|AUX)_LVL >'), self.__MatchAnalogInputGainSwitch, None)
            self.AddMatchString(re.compile(b'< REP 09 AUDIO_OUT_LVL_SWITCH (LINE|AUX|MIC)_LVL >'), self.__MatchAnalogOutputGainSwitch, None)
            self.AddMatchString(re.compile(b'< REP (0[1-9]|10) AUDIO_GAIN_HI_RES ([0-9]{4}) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP (0[1-9]|10) AUDIO_MUTE (ON|OFF) >'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'< REP ONHOOK_ENABLE ON >'), self.__MatchCallStatus, 'Enabled')
            self.AddMatchString(re.compile(b'< REP ONHOOK_STATE (ON|OFF)HOOK >'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_AUDIO_MUTE (ON|OFF) >'), self.__MatchDeviceAudioMute, None)
            self.AddMatchString(re.compile(b'< REP LOGIC_MUTE (ON|OFF) >'), self.__MatchLogicMute, None)
            self.AddMatchString(re.compile(b'< REP (0[1-6]) MATRIX_MXR_GAIN (0[7-9]|10) ([0-9]{4}) >'), self.__MatchMatrixMixerGain, None)
            self.AddMatchString(re.compile(b'< REP (0[1-6]) MATRIX_MXR_ROUTE (0[7-9]|10) (ON|OFF) >'), self.__MatchMatrixMixerRouting, None)
            self.AddMatchString(re.compile(b'< REP PRESET (0[0-9]|10) >'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)
            
    def SetAnalogInputGainSwitch(self, value, qualifier):

        ValueStateValues = {
            'Line Level' : '< SET 05 AUDIO_IN_LVL_SWITCH LINE_LVL >', 
            'AUX Level'  : '< SET 05 AUDIO_IN_LVL_SWITCH AUX_LVL >'
        }

        AnalogInputGainSwitchCmdString = ValueStateValues[value]
        self.__SetHelper('AnalogInputGainSwitch', AnalogInputGainSwitchCmdString, value, qualifier)

    def UpdateAnalogInputGainSwitch(self, value, qualifier):

        AnalogInputGainSwitchCmdString = '< GET 05 AUDIO_IN_LVL_SWITCH >'
        self.__UpdateHelper('AnalogInputGainSwitch', AnalogInputGainSwitchCmdString, value, qualifier)

    def __MatchAnalogInputGainSwitch(self, match, tag):

        ValueStateValues = {
            'LINE' : 'Line Level', 
            'AUX'  : 'AUX Level'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AnalogInputGainSwitch', value, None)

    def SetAnalogOutputGainSwitch(self, value, qualifier):

        ValueStateValues = {
            'Line Level' : '< SET 09 AUDIO_OUT_LVL_SWITCH LINE_LVL >', 
            'AUX Level'  : '< SET 09 AUDIO_OUT_LVL_SWITCH AUX_LVL >', 
            'MIC Level'  : '< SET 09 AUDIO_OUT_LVL_SWITCH MIC_LVL >'
        }

        AnalogOutputGainSwitchCmdString = ValueStateValues[value]
        self.__SetHelper('AnalogOutputGainSwitch', AnalogOutputGainSwitchCmdString, value, qualifier)

    def UpdateAnalogOutputGainSwitch(self, value, qualifier):

        AnalogOutputGainSwitchCmdString = '< GET 09 AUDIO_OUT_LVL_SWITCH >'
        self.__UpdateHelper('AnalogOutputGainSwitch', AnalogOutputGainSwitchCmdString, value, qualifier)

    def __MatchAnalogOutputGainSwitch(self, match, tag):

        ValueStateValues = {
            'LINE' : 'Line Level', 
            'AUX'  : 'AUX Level', 
            'MIC'  : 'MIC Level'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AnalogOutputGainSwitch', value, None)

    def SetAudioGain(self, value, qualifier):

        ChannelStates = {
            'All'            : '00', 
            'Dante Input 1'  : '01', 
            'Dante Input 2'  : '02', 
            'Dante Input 3'  : '03', 
            'Dante Input 4'  : '04', 
            'Analog Input'   : '05', 
            'USB Input'      : '06', 
            'Dante Output 1' : '07', 
            'Dante Output 2' : '08', 
            'Analog Output'  : '09', 
            'USB Output'     : '10'
        }

        ValueConstraints = {
            'Min' : -110,
            'Max' : 30
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ChannelStates:
            temp_val = (value + 110) * 10
            AudioGainCmdString = '< SET {} AUDIO_GAIN_HI_RES {:04d} >'.format(ChannelStates[channel_val], int(temp_val))
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        ChannelStates = {
            'Dante Input 1'  : '01', 
            'Dante Input 2'  : '02', 
            'Dante Input 3'  : '03', 
            'Dante Input 4'  : '04', 
            'Analog Input'   : '05', 
            'USB Input'      : '06', 
            'Dante Output 1' : '07', 
            'Dante Output 2' : '08', 
            'Analog Output'  : '09', 
            'USB Output'     : '10'
        }
        
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            AudioGainCmdString = '< GET {} AUDIO_GAIN_HI_RES >'.format(ChannelStates[channel_val])
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        ChannelStates = {
            1 : 'Dante Input 1', 
            2 : 'Dante Input 2', 
            3 : 'Dante Input 3', 
            4 : 'Dante Input 4', 
            5 : 'Analog Input', 
            6 : 'USB Input', 
            7 : 'Dante Output 1', 
            8 : 'Dante Output 2', 
            9 : 'Analog Output', 
            10: 'USB Output'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[int(match.group(1).decode())]
        value = (int(match.group(2).decode())/10) - 110.0
        self.WriteStatus('AudioGain', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            'All'            : '00', 
            'Dante Input 1'  : '01', 
            'Dante Input 2'  : '02', 
            'Dante Input 3'  : '03', 
            'Dante Input 4'  : '04', 
            'Analog Input'   : '05', 
            'USB Input'      : '06', 
            'Dante Output 1' : '07', 
            'Dante Output 2' : '08', 
            'Analog Output'  : '09', 
            'USB Output'     : '10'
        }

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            AudioMuteCmdString = '< SET {} AUDIO_MUTE {} >'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'Dante Input 1'  : '01', 
            'Dante Input 2'  : '02', 
            'Dante Input 3'  : '03', 
            'Dante Input 4'  : '04', 
            'Analog Input'   : '05', 
            'USB Input'      : '06', 
            'Dante Output 1' : '07', 
            'Dante Output 2' : '08', 
            'Analog Output'  : '09', 
            'USB Output'     : '10'
        }
        
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            AudioMuteCmdString = '< GET {} AUDIO_MUTE >'.format(ChannelStates[channel_val])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ChannelStates = {
            1 : 'Dante Input 1', 
            2 : 'Dante Input 2', 
            3 : 'Dante Input 3', 
            4 : 'Dante Input 4', 
            5 : 'Analog Input', 
            6 : 'USB Input', 
            7 : 'Dante Output 1', 
            8 : 'Dante Output 2', 
            9 : 'Analog Output', 
            10: 'USB Output'
        }

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[int(match.group(1).decode())]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def UpdateCallStatus(self, value, qualifier):

        if self.call_status_enabled:
            CallStatusCmdString = '< GET ONHOOK_STATE >'
        else:
            CallStatusCmdString = '< SET ONHOOK_ENABLE ON >'
        self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)

    def __MatchCallStatus(self, match, tag):

        if tag is None:
            ValueStateValues = {
                'ON': 'Inactive',
                'OFF': 'Active'
            }

            value = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('CallStatus', value, None)
        else:
            self.call_status_enabled = True

    def SetDeviceAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '< SET DEVICE_AUDIO_MUTE ON >', 
            'Off' : '< SET DEVICE_AUDIO_MUTE OFF >'
        }

        DeviceAudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('DeviceAudioMute', DeviceAudioMuteCmdString, value, qualifier)

    def UpdateDeviceAudioMute(self, value, qualifier):

        DeviceAudioMuteCmdString = '< GET DEVICE_AUDIO_MUTE >'
        self.__UpdateHelper('DeviceAudioMute', DeviceAudioMuteCmdString, value, qualifier)

    def __MatchDeviceAudioMute(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceAudioMute', value, None)

    def SetLogicMute(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]
            

        if value in ValueStateValues:
            LogicMuteCmdString = '< SET LOGIC_MUTE {} >'.format(value.upper())
            self.__SetHelper('LogicMute', LogicMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogicMute')

    def UpdateLogicMute(self, value, qualifier):

        LogicMuteCmdString = '< GET LOGIC_MUTE >'
        self.__UpdateHelper('LogicMute', LogicMuteCmdString, value, qualifier)

    def __MatchLogicMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('LogicMute', value, None)

    def SetMatrixMixerGain(self, value, qualifier):

        InputStates = {
            'All'     : '00', 
            'Dante 1' : '01', 
            'Dante 2' : '02', 
            'Dante 3' : '03', 
            'Dante 4' : '04', 
            'Analog'  : '05', 
            'USB'     : '06'
        }

        OutputStates = {
            'All'     : '00', 
            'Dante 1' : '07', 
            'Dante 2' : '08', 
            'Analog'  : '09', 
            'USB'     : '10'
        }

        ValueConstraints = {
            'Min' : -110,
            'Max' : 30
            }

        input_val = qualifier['Input']
        otput_val = qualifier['Output']
        MatrixMixerGainCmdString = ''
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and input_val in InputStates and otput_val in OutputStates:
            temp_val = (value + 110) * 10
            if input_val == 'USB' and otput_val != 'USB':
                MatrixMixerGainCmdString = '< SET 06 MATRIX_MXR_GAIN {} {:04d} >'.format(OutputStates[otput_val], int(temp_val))
            else:
                MatrixMixerGainCmdString = '< SET {} MATRIX_MXR_GAIN {} {:04d} >'.format(InputStates[input_val], OutputStates[otput_val], int(temp_val))
            if MatrixMixerGainCmdString:
                self.__SetHelper('MatrixMixerGain', MatrixMixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerGain')

    def UpdateMatrixMixerGain(self, value, qualifier):

        InputStates = {
            'Dante 1' : '01', 
            'Dante 2' : '02', 
            'Dante 3' : '03', 
            'Dante 4' : '04', 
            'Analog'  : '05', 
            'USB'     : '06'
        }

        OutputStates = {
            'Dante 1' : '07', 
            'Dante 2' : '08', 
            'Analog'  : '09', 
            'USB'     : '10'
        }
        input_val = qualifier['Input']
        otput_val = qualifier['Output']
        if input_val in InputStates and otput_val in OutputStates:
            if input_val == 'USB' and otput_val != 'USB':
                MatrixMixerGainCmdString = '< GET 06 MATRIX_MXR_GAIN {} >'.format(OutputStates[otput_val])
            else:
                MatrixMixerGainCmdString = '< GET {} MATRIX_MXR_GAIN {} >'.format(InputStates[input_val], OutputStates[otput_val])
            self.__UpdateHelper('MatrixMixerGain', MatrixMixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerGain')

    def __MatchMatrixMixerGain(self, match, tag):

        InputStates = {
            1 : 'Dante 1', 
            2 : 'Dante 2', 
            3 : 'Dante 3', 
            4 : 'Dante 4', 
            5 : 'Analog', 
            6 : 'USB'
        }

        OutputStates = {
            7 : 'Dante 1', 
            8 : 'Dante 2', 
            9 : 'Analog', 
            10: 'USB'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[int(match.group(1).decode())]
        qualifier['Output'] = OutputStates[int(match.group(2).decode())]
        value = (int(match.group(3).decode())/10) - 110.0
        self.WriteStatus('MatrixMixerGain', value, qualifier)

    def SetMatrixMixerRouting(self, value, qualifier):

        InputStates = {
            'All'     : '00', 
            'Dante 1' : '01', 
            'Dante 2' : '02', 
            'Dante 3' : '03', 
            'Dante 4' : '04', 
            'Analog'  : '05', 
            'USB'     : '06'
        }

        OutputStates = {
            'All'     : '00', 
            'Dante 1' : '07', 
            'Dante 2' : '08', 
            'Analog'  : '09', 
            'USB'     : '10'
        }

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF'
        }

        input_val = qualifier['Input']
        otput_val = qualifier['Output']
        MatrixMixerRoutingCmdString = ''
        if input_val in InputStates and otput_val in OutputStates:
            if input_val == 'USB' and otput_val != 'USB':
                MatrixMixerRoutingCmdString = '< SET 06 MATRIX_MXR_ROUTE {} {} >'.format(OutputStates[otput_val], ValueStateValues[value])
            else:
                MatrixMixerRoutingCmdString = '< SET {} MATRIX_MXR_ROUTE {} {} >'.format(InputStates[input_val], OutputStates[otput_val], ValueStateValues[value])
            if MatrixMixerRoutingCmdString:
                self.__SetHelper('MatrixMixerRouting', MatrixMixerRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerRouting')

    def UpdateMatrixMixerRouting(self, value, qualifier):

        InputStates = {
            'Dante 1' : '01', 
            'Dante 2' : '02', 
            'Dante 3' : '03', 
            'Dante 4' : '04', 
            'Analog'  : '05', 
            'USB'     : '06'
        }

        OutputStates = {
            'Dante 1' : '07', 
            'Dante 2' : '08', 
            'Analog'  : '09', 
            'USB'     : '10'
        }
        
        input_val = qualifier['Input']
        otput_val = qualifier['Output']
        if input_val in InputStates and otput_val in OutputStates:
            if input_val == 'USB' and otput_val != 'USB':
                MatrixMixerRoutingCmdString = '< GET 06 MATRIX_MXR_ROUTE {} >'.format(InputStates[input_val], OutputStates[otput_val])
            else:
                MatrixMixerRoutingCmdString = '< GET {} MATRIX_MXR_ROUTE {} >'.format(InputStates[input_val], OutputStates[otput_val])
            self.__UpdateHelper('MatrixMixerRouting', MatrixMixerRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerRouting')

    def __MatchMatrixMixerRouting(self, match, tag):

        InputStates = {
            1 : 'Dante 1', 
            2 : 'Dante 2', 
            3 : 'Dante 3', 
            4 : 'Dante 4', 
            5 : 'Analog', 
            6 : 'USB'
        }

        OutputStates = {
            7 : 'Dante 1', 
            8 : 'Dante 2', 
            9 : 'Analog', 
            10: 'USB'
        }

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[int(match.group(1).decode())]
        qualifier['Output'] = OutputStates[int(match.group(2).decode())]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MatrixMixerRouting', value, qualifier)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            '1' : '< SET PRESET 01 >', 
            '2' : '< SET PRESET 02 >', 
            '3' : '< SET PRESET 03 >', 
            '4' : '< SET PRESET 04 >', 
            '5' : '< SET PRESET 05 >', 
            '6' : '< SET PRESET 06 >', 
            '7' : '< SET PRESET 07 >', 
            '8' : '< SET PRESET 08 >', 
            '9' : '< SET PRESET 09 >', 
            '10': '< SET PRESET 10 >'
        }

        PresetCmdString = ValueStateValues[value]
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = '< GET PRESET >'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        ValueStateValues  = {
            0  : 'Not Loaded',
            1  : '1',
            2  : '2',
            3  : '3',
            4  : '4',
            5  : '5',
            6  : '6',
            7  : '7',
            8  : '8',
            9  : '9',
            10 : '10'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('Preset', value, None)

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

        self.Error(['Error Occurred'])
        
    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.call_status_enabled = False

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