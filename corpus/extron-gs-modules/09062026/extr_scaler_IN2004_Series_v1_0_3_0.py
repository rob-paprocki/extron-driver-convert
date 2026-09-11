# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, search

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
            'IN2004': self.extr_17_17181_2004,
            'DTP3 IN2004 DI/DO': self.extr_17_17181_DIDO,
            'DTP3 IN2004 DO': self.extr_17_17181_DTP3
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'AudioFormat': {'Parameters': ['Input'], 'Status': {}},
            'AudioOutputMute': {'Parameters': ['Output'], 'Status': {}},
            'ImageReset': { 'Status': {}},
            'AutoSwitchMode': { 'Status': {}},
            'CECAudioMute': {'Parameters': ['Output'], 'Status': {}},
            'CECPower': {'Parameters': ['Output'], 'Status': {}},
            'CECShowAsActiveSource': {'Parameters': ['Output'], 'Status': {}},
            'CECVolume': {'Parameters': ['Output'], 'Status': {}},
            'ContactStatus': {'Parameters': ['Port'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'GroupLineMute': { 'Status': {}},
            'GroupLineVolume': { 'Status': {}},
            'GroupOutputMute': { 'Status': {}},
            'GroupOutputVolume': { 'Status': {}},
            'GroupProgramBass': { 'Status': {}},
            'GroupProgramMute': { 'Status': {}},
            'GroupProgramTreble': { 'Status': {}},
            'GroupProgramVolume': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'Input': { 'Status': {}},
            'InputPresetRecall': { 'Status': {}},
            'InputPresetSave': { 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'LineInputGain': {'Parameters': ['Input'], 'Status': {}},
            'LineInputMute': {'Parameters': ['Input'], 'Status': {}},
            'LineMixLevel': {'Parameters': ['Line'], 'Status': {}},
            'LineMixMute': {'Parameters': ['Line'], 'Status': {}},
            'Logo': { 'Status': {}},
            'LoopOut': { 'Status': {}},
            'OutputAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'OutputFormat': {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'PowerSaveMode': { 'Status': {}},
            'ProgramInputGain': {'Parameters': ['Input'], 'Status': {}},
            'ProgramInputMute': {'Parameters': ['Input'], 'Status': {}},
            'ScreenSaverStatus': { 'Status': {}},
            'Tally': {'Parameters': ['Port'], 'Status': {}},
            'Temperature': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}}
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.CECOutputList = []
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH
            self.AddMatchString(compile(b'DsM6000([0-3])\*([0-1])\r\n'), self.__MatchAudioOutputMute, None)
            self.AddMatchString(compile(b'DsG6000([0-3])\*([0-9 -]{1,5})\r\n'), self.__MatchOutputAttenuation, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchInputSwitch, None)
            self.AddMatchString(compile(b'Aspr([1-4])\*(1|2)\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'AfmtI([1-4])\*([0-5])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(compile(b'Cntc([01 ]{13})\r\n'), self.__MatchContactStatus, None)
            self.AddMatchString(compile(b'Cntc([1-7])\*(0|1)\r\n'), self.__MatchContactStatus, 'Unsolicited')
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frz1\*(0|1)\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'Mut([0-2]) ([0-2]) ?([0-2])?\r\n'), self.__MatchGlobalVideoMute, None)
            self.AddMatchString(compile(b'Vmt([0-2])\r\n'), self.__MatchGlobalVideoMute, 'Unsolicited')
            self.AddMatchString(compile(b'GrpmD6\*([01])\r\n'), self.__MatchGroupLineMute, None)
            self.AddMatchString(compile(b'GrpmD5\*([0-9-]{1,5})\r\n'), self.__MatchGroupLineVolume, None)
            self.AddMatchString(compile(b'GrpmD10\*([01])\r\n'), self.__MatchGroupOutputMute, None)
            self.AddMatchString(compile(b'GrpmD9\*([0-9-]{1,5})\r\n'), self.__MatchGroupOutputVolume, None)
            self.AddMatchString(compile(b'GrpmD7\*([0-9-]{1,4})\r\n'), self.__MatchGroupProgramBass, None)
            self.AddMatchString(compile(b'GrpmD4\*([01])\r\n'), self.__MatchGroupProgramMute, None)
            self.AddMatchString(compile(b'GrpmD8\*([0-9-]{1,4})\r\n'), self.__MatchGroupProgramTreble, None)
            self.AddMatchString(compile(b'GrpmD3\*([0-9-]{1,5})\r\n'), self.__MatchGroupProgramVolume, None)
            self.AddMatchString(compile(b'HdcpE([1-4])\*(0|1)'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpI([1-4])\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO(1|2|3)\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'In([1-4]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'In00 (0|1)\*(0|1)\*(0|1)\*(0|1)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'DsG(4000[012])\*([0-9-]{1,4})\r\n'), self.__MatchLineInputGain, None)
            self.AddMatchString(compile(b'DsM(4000[012])\*([01])\r\n'), self.__MatchLineInputMute, None)
            self.AddMatchString(compile(b'DsG4010([01])\*([0-9-]{1,5})\r\n'), self.__MatchLineMixLevel, None)
            self.AddMatchString(compile(b'DsM4010([01])\*([01])\r\n'), self.__MatchLineMixMute, None)
            self.AddMatchString(compile(b'LogoE1\*([0-9]|1[0-6])\r\n'), self.__MatchLogo, None)
            self.AddMatchString(compile(b'Lout([0-4])\r\n'), self.__MatchLoopOut, None)
            self.AddMatchString(compile(b'Vtpo(1|2|3)\*([0123579][0]?)\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(compile(b'Rate1\*([0-9]{3})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(compile(b'Psav(0|1|2|9)\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(compile(b'DsG3000([0-7])\*([0-9 -]{1,5})\r\n'), self.__MatchProgramInputGain, None)
            self.AddMatchString(compile(b'DsM3000([0-7])\*([0-1])\r\n'), self.__MatchProgramInputMute, None)
            self.AddMatchString(compile(b'SsavS1\*([0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(compile(b'Taly([01 ]{13})\r\n'), self.__MatchTally, None)
            self.AddMatchString(compile(b'Taly([1-7])\*(0|1)\r\n'), self.__MatchTally, 'Unsolicited')
            self.AddMatchString(compile(b'28Stat ([0-9][0-9]\.[0-9])C\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'Test1\*0?([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(b'Vmt(1|2|3)\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'E([0-3][0-8])\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def __MatchInputSwitch(self, match, tag):

        self.UpdateInput(None, None)
        self.UpdateLoopOut(None, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill':   '1',
            'Follow': '2',
        }

        if 1 <= int(qualifier['Input']) <= 4:
            AspectRatioCmdString = 'w{0}*{1}ASPR\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            commandString = 'w{0}ASPR\r'.format(qualifier['Input'])
            self.__UpdateHelper('AspectRatio', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1': 'Fill',
            '2': 'Follow',
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioFormat(self, value, qualifier):


        if 1 <= int(qualifier['Input']) <= 4 and value in self.AudioFormatStates:
            AudioFormatCmdString = 'wI{0}*{1}AFMT\r'.format(qualifier['Input'], self.AudioFormatStates[value])
            self.__SetHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            AudioFormatCmdString = 'wI{0}AFMT\r'.format(qualifier['Input'])
            self.__UpdateHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioFormat')

    def __MatchAudioFormat(self, match, tag):

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = self.AudioFormatStateValues[match.group(2).decode()]
        self.WriteStatus('AudioFormat', value, qualifier)

    def SetAudioOutputMute(self, value, qualifier):

        muteValues = {
            'On': '1',
            'Off': '0',
        }

        outputdict = {
            'HDMI/DTP Output': [0,1],
            'Line Out 1': 2,
            'Line Out 2': 3
        }

        if qualifier['Output'] in outputdict:
            if qualifier['Output'] == 'HDMI/DTP Output':
                self.__SetHelper('AudioOutputMute', 'WM6000{0}*{1}AU\r'.format(outputdict[qualifier['Output']][0], muteValues[value]), value, qualifier)
                self.__SetHelper('AudioOutputMute', 'WM6000{0}*{1}AU\r'.format(outputdict[qualifier['Output']][1], muteValues[value]), value, qualifier)
            else:
                self.__SetHelper('AudioOutputMute', 'WM6000{0}*{1}AU\r'.format(outputdict[qualifier['Output']], muteValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputMute')

    def UpdateAudioOutputMute(self, value, qualifier):

        outputdict = {
            'HDMI/DTP Output': 0,
            'Line Out 1': 2,
            'Line Out 2': 3
        }
        AudioOutputMuteCmdString = 'WM6000{0}AU\r'.format(outputdict[qualifier['Output']])
        self.__UpdateHelper('AudioOutputMute', AudioOutputMuteCmdString, value, qualifier)

    def __MatchAudioOutputMute(self, match, tag):

        muteValues = {
            '1': 'On',
            '0': 'Off'
        }

        outputdict = {
            '0': 'HDMI/DTP Output',
            '1': 'HDMI/DTP Output',
            '2': 'Line Out 1',
            '3': 'Line Out 2'
        }

        qualifier = {}
        qualifier['Output'] = outputdict[match.group(1).decode()]
        value = muteValues[match.group(2).decode()]
        self.WriteStatus('AudioOutputMute', value, qualifier)

    def SetImageReset(self, value, qualifier):

        ValueStateValues = {
            'Execute':            '0',
            'Execute and Fill':   '1',
            'Execute and Follow': '2',
        }

        ImageResetCmdString = '1*{0}A'.format(ValueStateValues[value])
        self.__SetHelper('ImageReset', ImageResetCmdString, value, qualifier)

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeStateValues = {
             'User Defined Priority': 'w1AUSW\r',
             'Last Connected Input':  'w2AUSW\r',
             'Off':                   'w0AUSW\r',
        }

        AutoSwitchModeCmdString = AutoSwitchModeStateValues[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, qualifier):

        AutoSwitchModeStateNames = {
            '0': 'Off',
            '1': 'User Defined Priority',
            '2': 'Last Connected Input',
        }

        AutoSwitchModeCmdString = AutoSwitchModeStateNames[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', AutoSwitchModeCmdString, qualifier)

    def SetCECAudioMute(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            output = self.OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))
            CECAudioMuteCmdString = 'wO{}*%44%43DCEC\r'.format(output)
            self.__SetHelper('CECAudioMute', CECAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECAudioMute')

    def SetCECPower(self, value, qualifier):

        ValueStateValues = {
            'On' : '%04',
            'Off' : '%36'
        }

        if qualifier['Output'] in self.OutputStates and value in ValueStateValues:
            output = self.OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECPowerCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECPower', CECPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECShowAsActiveSource(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            output = self.OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECShowAsActiveSourceCmdString = 'wO{}*\"ShowMe\"DCEC\r'.format(output)
            self.__SetHelper('CECShowAsActiveSource', CECShowAsActiveSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECShowAsActiveSource')

    def SetCECVolume(self, value, qualifier):

        ValueStateValues = {
            'Up' : '%44%41',
            'Down' : '%44%42'
        }

        if qualifier['Output'] in self.OutputStates and value in ValueStateValues:
            output = self.OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECVolumeCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECVolume', CECVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECVolume')

    def UpdateContactStatus(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= 7:
            ContactStatusCmdString = 'wCNTC\r'
            self.__UpdateHelper('ContactStatus', ContactStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateContactStatus')

    def __MatchContactStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Closed',
        }

        if tag == 'Unsolicited':
            qualifier = {'Port': match.group(1).decode()}
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('ContactStatus', value, qualifier)
        else:
            values = match.group(1).decode().split()
            port = 1
            for i in values:
                self.WriteStatus('ContactStatus', ValueStateValues[i], {'Port': str(port)})
                port += 1

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':    '0',
            'Mode 1': '1',
            'Mode 2': '2',
        }

        ExecutiveModeCmdString = '{0}X'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        FreezeCmdString = '1*{0}F'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):


        FreezeCmdString = '1F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video Mute': '1',
            'Sync Mute': '2',
            'Off': '0',
        }

        GlobalVideoMuteCmdString = '{0}B'.format(ValueStateValues[value])
        self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def UpdateGlobalVideoMute(self, value, qualifier):

        GlobalVideoMuteCmdString = 'wVM\r'
        self.__UpdateHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def __MatchGlobalVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'Video Mute',
            '2': 'Sync Mute',
            '0': 'Off',
        }

        if tag == 'Unsolicited':
            value = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('GlobalVideoMute', value, None)

            self.WriteStatus('VideoMute', value, {'Output': '1A'})
            self.WriteStatus('VideoMute', value, {'Output': '1B'})
            self.WriteStatus('VideoMute', value, {'Output': '1C'})
        else:
            try:
                value1 = ValueStateValues[match.group(1).decode()]
                value2 = ValueStateValues[match.group(2).decode()]
                value3 = ValueStateValues[match.group(3).decode()]
                if value1 == value2 == value3:
                    self.WriteStatus('GlobalVideoMute', value1, None)
                self.WriteStatus('VideoMute', value1, {'Output': '1A'})
                self.WriteStatus('VideoMute', value2, {'Output': '1B'})
                self.WriteStatus('VideoMute', value3, {'Output': '1C'})
            except AttributeError:
                if value1 == value2:
                    self.WriteStatus('GlobalVideoMute', value1, None)
                self.WriteStatus('VideoMute', value1, {'Output': '1A'})
                self.WriteStatus('VideoMute', value2, {'Output': '1B'})

    def SetGroupLineMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        GroupLineMuteCmdString = 'wD6*{0}GRPM\r'.format(ValueStateValues[value])
        self.__SetHelper('GroupLineMute', GroupLineMuteCmdString, value, qualifier)

    def UpdateGroupLineMute(self, value, qualifier):

        GroupLineMuteCmdString = 'wD6GRPM\r'
        self.__UpdateHelper('GroupLineMute', GroupLineMuteCmdString, value, qualifier)

    def __MatchGroupLineMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GroupLineMute', value, None)

    def SetGroupLineVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -100,
            'Max' : 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupLineVolumeCmdString = 'wD5*{0}GRPM\r'.format(round(value*10))
            self.__SetHelper('GroupLineVolume', GroupLineVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLineVolume')

    def UpdateGroupLineVolume(self, value, qualifier):

        GroupLineVolumeCmdString = 'wD5GRPM\r'
        self.__UpdateHelper('GroupLineVolume', GroupLineVolumeCmdString, value, qualifier)

    def __MatchGroupLineVolume(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupLineVolume', value, None)

    def SetGroupOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        GroupOutputMuteCmdString = 'wD10*{0}GRPM\r'.format(ValueStateValues[value])
        self.__SetHelper('GroupOutputMute', GroupOutputMuteCmdString, value, qualifier)

    def UpdateGroupOutputMute(self, value, qualifier):

        GroupOutputMuteCmdString = 'wD10GRPM\r'
        self.__UpdateHelper('GroupOutputMute', GroupOutputMuteCmdString, value, qualifier)

    def __MatchGroupOutputMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GroupOutputMute', value, None)

    def SetGroupOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -100,
            'Max' : 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupOutputVolumeCmdString = 'wD9*{0}GRPM\r'.format(round(value*10))
            self.__SetHelper('GroupOutputVolume', GroupOutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupOutputVolume')

    def UpdateGroupOutputVolume(self, value, qualifier):

        GroupOutputVolumeCmdString = 'wD9GRPM\r'
        self.__UpdateHelper('GroupOutputVolume', GroupOutputVolumeCmdString, value, qualifier)

    def __MatchGroupOutputVolume(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupOutputVolume', value, None)

    def SetGroupProgramBass(self, value, qualifier):

        ValueConstraints = {
            'Min' : -24,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupProgramBassCmdString = 'wD7*{0}GRPM\r'.format(round(value*10))
            self.__SetHelper('GroupProgramBass', GroupProgramBassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupProgramBass')

    def UpdateGroupProgramBass(self, value, qualifier):

        GroupProgramBassCmdString = 'wD7GRPM\r'
        self.__UpdateHelper('GroupProgramBass', GroupProgramBassCmdString, value, qualifier)

    def __MatchGroupProgramBass(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupProgramBass', value, None)

    def SetGroupProgramMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        GroupProgramMuteCmdString = 'wD4*{0}GRPM\r'.format(ValueStateValues[value])
        self.__SetHelper('GroupProgramMute', GroupProgramMuteCmdString, value, qualifier)

    def UpdateGroupProgramMute(self, value, qualifier):

        GroupProgramMuteCmdString = 'wD4GRPM\r'
        self.__UpdateHelper('GroupProgramMute', GroupProgramMuteCmdString, value, qualifier)

    def __MatchGroupProgramMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GroupProgramMute', value, None)

    def SetGroupProgramTreble(self, value, qualifier):

        ValueConstraints = {
            'Min' : -24,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupProgramTrebleCmdString = 'wD8*{0}GRPM\r'.format(round(value*10))
            self.__SetHelper('GroupProgramTreble', GroupProgramTrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupProgramTreble')

    def UpdateGroupProgramTreble(self, value, qualifier):

        GroupProgramTrebleCmdString = 'wD8GRPM\r'
        self.__UpdateHelper('GroupProgramTreble', GroupProgramTrebleCmdString, value, qualifier)

    def __MatchGroupProgramTreble(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupProgramTreble', value, None)

    def SetGroupProgramVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -100,
            'Max' : 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupProgramVolume = 'wD3*{0}GRPM\r'.format(round(value*10))
            self.__SetHelper('GroupProgramVolume', GroupProgramVolume, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupProgramVolume')

    def UpdateGroupProgramVolume(self, value, qualifier):

        GroupProgramVolume = 'wD3GRPM\r'
        self.__UpdateHelper('GroupProgramVolume', GroupProgramVolume, value, qualifier)

    def __MatchGroupProgramVolume(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupProgramVolume', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if 1 <= int(qualifier['Input']) <= 4:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            HDCPInputAuthorizationCmdString = 'wE{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            HDCPInputStatusCmdString = 'wI{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Device Detected',
            '1': 'Source Detected with HDCP',
            '2': 'Source Detected without HDCP',
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        output_ = qualifier['Output']
        if output_ in self.OutputStates:
            HDCPOutputStatusCmdString = 'wO{0}HDCP\r'.format(self.OutputStates[output_])
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sink Device Detected',
            '1': 'Sink Detected with HDCP',
            '2': 'Sink Detected without HDCP',
        }

        qualifier = {}
        qualifier['Output'] = self.OutputStateValues[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetInput(self, value, qualifier):

        if 1 <= int(value) <= 4:
            InputCmdString = '{0}!'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            InputSignalStatusCmdString = 'w0LS\r'
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active',
        }

        for i in range(1, 5):
            value = match.group(i).decode()
            qualifier = {'Input': str(i)}
            value = ValueStateValues[value]
            self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetLineInputGain(self, value, qualifier):

        InputStates = {
            'Line In 1'   : '40000',
            'Line In 2'   : '40001',
            'File Player' : ['40002', '40003']
        }

        ValueConstraints = {
            'Min' : -18,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if qualifier['Input'] in ['File Player']:
                self.__SetHelper('LineInputGain', 'wG{0}*{1}AU\r'.format(InputStates[qualifier['Input']][0], round(value*10)), value, qualifier, 3)
                self.__SetHelper('LineInputGain', 'wG{0}*{1}AU\r'.format(InputStates[qualifier['Input']][1], round(value*10)), value, qualifier, 3)
            else:
                self.__SetHelper('LineInputGain', 'wG{0}*{1}AU\r'.format(InputStates[qualifier['Input']], round(value*10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        InputStates = {
            'Line In 1'   : '40000',
            'Line In 2'   : '40001',
            'File Player' : '40002'
        }

        LineInputGainCmdString = 'wG{0}AU\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('LineInputGain', LineInputGainCmdString, value, qualifier)

    def __MatchLineInputGain(self, match, tag):

        InputStates = {
            '40000' : 'Line In 1',
            '40001' : 'Line In 2',
            '40002' : 'File Player'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode())/10
        self.WriteStatus('LineInputGain', value, qualifier)

    def SetLineInputMute(self, value, qualifier):

        InputStates = {
            'Line In 1'   : '40000',
            'Line In 2'   : '40001',
            'File Player' : ['40002', '40003']
        }

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        if qualifier['Input'] in ['File Player']:
            self.__SetHelper('LineInputMute', 'wM{0}*{1}AU\r'.format(InputStates[qualifier['Input']][0], ValueStateValues[value]), value, qualifier) # per PD, send L/R commands back-to-back
            self.__SetHelper('LineInputMute', 'wM{0}*{1}AU\r'.format(InputStates[qualifier['Input']][1], ValueStateValues[value]), value, qualifier)
        else:
            self.__SetHelper('LineInputMute', 'wM{0}*{1}AU\r'.format(InputStates[qualifier['Input']], ValueStateValues[value]), value, qualifier)

    def UpdateLineInputMute(self, value, qualifier):

        InputStates = {
            'Line In 1'   : '40000',
            'Line In 2'   : '40001',
            'File Player' : '40002'
        }

        LineInputMuteCmdString = 'wM{0}AU\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('LineInputMute', LineInputMuteCmdString, value, qualifier)

    def __MatchLineInputMute(self, match, tag):

        InputStates = {
            '40000' : 'Line In 1',
            '40001' : 'Line In 2',
            '40002' : 'File Player'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LineInputMute', value, qualifier)

    def SetLineMixLevel(self, value, qualifier):

        LineStates = {
            '1': '0',
            '2': '1'
        }
        line = qualifier['Line']

        if line in LineStates and -100 <= value <= 12:
            LineMixLevelCmdString = 'wG4010{0}*{1}AU\r'.format(LineStates[line], round(value * 10))
            self.__SetHelper('LineMixLevel', LineMixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineMixLevel')

    def UpdateLineMixLevel(self, value, qualifier):

        LineStates = {
            '1': '0',
            '2': '1'
        }
        line = qualifier['Line']

        if line in LineStates:
            LineMixLevelCmdString = 'wG4010{0}AU\r'.format(LineStates[line])
            self.__UpdateHelper('LineMixLevel', LineMixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineMixLevel')

    def __MatchLineMixLevel(self, match, tag):

        LineStates = {
            '0': '1',
            '1': '2'
        }

        qualifier = {
            'Line': LineStates[match.group(1).decode()]
        }

        value = int(match.group(2).decode()) / 10
        if -100 <= value <= 12:
            self.WriteStatus('LineMixLevel', value, qualifier)

    def SetLineMixMute(self, value, qualifier):

        LineStates = {
            '1': '0',
            '2': '1'
        }
        line = qualifier['Line']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if line in LineStates and value in ValueStateValues:
            LineMixMuteCmdString = 'wM4010{0}*{1}AU\r'.format(LineStates[line], ValueStateValues[value])
            self.__SetHelper('LineMixMute', LineMixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineMixMute')

    def UpdateLineMixMute(self, value, qualifier):

        LineStates = {
            '1': '0',
            '2': '1'
        }
        line = qualifier['Line']

        if line in LineStates:
            LineMixMuteCmdString = 'wM4010{0}AU\r'.format(LineStates[line])
            self.__UpdateHelper('LineMixMute', LineMixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineMixMute')

    def __MatchLineMixMute(self, match, tag):

        LineStates = {
            '0': '1',
            '1': '2'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Line': LineStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LineMixMute', value, qualifier)

    def SetLogo(self, value, qualifier):

        logo = 0 if value == 'Off' else int(value)
        if 0 <= logo <= 16:
            self.__SetHelper('Logo', 'wE1*{}LOGO\r'.format(logo), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        self.__UpdateHelper('Logo', 'wE1LOGO\r', value, qualifier)

    def __MatchLogo(self, match, qualifier):

        value = 'Off' if match.group(1).decode() == '0' else match.group(1).decode()
        self.WriteStatus('Logo', value, qualifier)

    def SetLoopOut(self, value, qualifier):

        ValueStateValues = {
            'Match Scaler': '0',
            '1':            '1',
            '2':            '2',
            '3':            '3',
            '4':            '4'
        }

        if value in ValueStateValues:
            LoopOutCmdString = 'w{}LOUT\r'.format(ValueStateValues[value])
            self.__SetHelper('LoopOut', LoopOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoopOut')

    def UpdateLoopOut(self, value, qualifier):

        LoopOutCmdString = 'wLOUT\r'
        self.__UpdateHelper('LoopOut', LoopOutCmdString, value, qualifier)

    def __MatchLoopOut(self, match, tag):

        ValueStateValues = {
            '0': 'Match Scaler',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LoopOut', value, None)

    def SetOutputAttenuation(self, value, qualifier):

        OutputAttenuationConstraints = {
            'Min': -100,
            'Max': 0,
        }

        outputdict = {
            'HDMI/DTP Output': [0,1],
            'Line Out 1': 2,
            'Line Out 2': 3
        }

        if OutputAttenuationConstraints['Min'] <= value <= OutputAttenuationConstraints['Max'] and qualifier['Output'] in outputdict:
            if qualifier['Output'] == 'HDMI/DTP Output':
                self.__SetHelper('OutputAttenuation', 'WG6000{0}*{1}AU\r'.format(outputdict[qualifier['Output']][0], round(value*10)), value, qualifier, 3)
                self.__SetHelper('OutputAttenuation', 'WG6000{0}*{1}AU\r'.format(outputdict[qualifier['Output']][1], round(value*10)), value, qualifier, 3)
            else:
                self.__SetHelper('OutputAttenuation', 'WG6000{0}*{1}AU\r'.format(outputdict[qualifier['Output']], round(value*10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAttenuation')

    def UpdateOutputAttenuation(self, value, qualifier):

        outputdict = {
            'HDMI/DTP Output': 0,
            'Line Out 1': 2,
            'Line Out 2': 3
        }

        if qualifier['Output'] in outputdict:
            OutputAttenuationCmdString = 'WG6000{0}AU\r'.format(outputdict[qualifier['Output']])
            self.__UpdateHelper('OutputAttenuation', OutputAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAttenuation')

    def __MatchOutputAttenuation(self, match, tag):

        outputdict = {
            '0': 'HDMI/DTP Output',
            '1': 'HDMI/DTP Output',
            '2': 'Line Out 1',
            '3': 'Line Out 2'
        }
        qualifier = {}
        qualifier['Output'] = outputdict[match.group(1).decode()]
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('OutputAttenuation', value, qualifier)

    def SetOutputFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto':                 '0',
            'DVI RGB 444':          '1',
            'HDMI RGB 444 Full':    '2',
            'HDMI RGB 444 Limited': '3',
            'YUV 444 Limited':      '5',
            'YUV 422 Limited':      '7'
        }

        output_ = qualifier['Output']
        if output_ in self.OutputStates:
            OutputFormatCmdString = 'w{0}*{1}VTPO\r'.format(self.OutputStates[output_], ValueStateValues[value])
            self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormat')

    def UpdateOutputFormat(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            OutputFormatCmdString = 'w{0}*VTPO\r'.format(self.OutputStates[qualifier['Output']])
            self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputFormat')

    def __MatchOutputFormat(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'DVI RGB 444',
            '2': 'HDMI RGB 444 Full',
            '3': 'HDMI RGB 444 Limited',
            '5': 'YUV 444 Limited',
            '7': 'YUV 422 Limited'
        }

        qualifier = {}
        qualifier['Output'] = self.OutputStateValues[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputFormat', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480 (60Hz)':           '10',
            '800x600 (60Hz)':           '11',
            '1024x768 (60Hz)':          '12',
            '1280x768 (60Hz)':          '13',
            '1280x800 (60Hz)':          '14',
            '1280x1024 (60Hz)':         '15',
            '1360x768 (60Hz)':          '16',
            '1366x768 (60Hz)':          '17',
            '1440x900 (60Hz)':          '18',
            '1400x1050 (60Hz)':         '19',
            '1600x900 (60Hz)':          '20',
            '1680x1050 (60Hz)':         '21',
            '1600x1200 (60Hz)':         '22',
            '1920x1200 (60Hz)':         '23',
            '480p (59.94Hz)':           '24',
            '480p (60Hz)':              '25',
            '576p (50Hz)':              '26',
            '720p (25Hz)':              '29',
            '720p (29.97Hz)':           '30',
            '720p (30Hz)':              '31',
            '720p (50Hz)':              '32',
            '720p (59.94Hz)':           '33',
            '720p (60Hz)':              '34',
            '1080p (23.98Hz)':          '38',
            '1080p (24Hz)':             '39',
            '1080p (25Hz)':             '40',
            '1080p (29.97Hz)':          '41',
            '1080p (30Hz)':             '42', 
            '1080p (50Hz)':             '43',
            '1080p (59.94Hz)':          '44',
            '1080p (60Hz)':             '45',
            '2048x1080 (2K) (23.98Hz)': '46',
            '2048x1080 (2K) (24Hz)':    '47',
            '2048x1080 (2K) (25Hz)':    '48',
            '2048x1080 (2K) (29.97Hz)': '49',
            '2048x1080 (2K) (30Hz)':    '50',
            '2048x1080 (2K) (50Hz)':    '51',
            '2048x1080 (2K) (59.94Hz)': '52',
            '2048x1080 (2K) (60Hz)':    '53',
            '2048x1200 (60Hz)':         '54',
            '2048x1536 (60Hz)':         '55',
            '2560x1080 (60Hz)':         '56',
            '2560x1440 (60Hz)':         '57',
            '2560x1600 (60Hz)':         '58',
            '3840x2160 (23.98Hz)':      '59',
            '3840x2160 (24Hz)':         '60',
            '3840x2160 (25Hz)':         '61',
            '3840x2160 (29.97Hz)':      '62',
            '3840x2160 (30Hz)':         '63',
            '3840x2160 (50Hz)':         '64',
            '3840x2160 (59.94Hz)':      '65',
            '3840x2160 (60Hz)':         '66',
            '4096x2160 (23.98Hz)':      '69',
            '4096x2160 (24Hz)':         '70',
            '4096x2160 (25Hz)':         '71',
            '4096x2160 (29.97Hz)':      '72',
            '4096x2160 (30Hz)':         '73',
            '4096x2160 (50Hz)':         '74',
            '4096x2160 (59.94Hz)':      '75',
            '4096x2160 (60Hz)':         '76',
            'Custom 1':                 '201',
            'Custom 2':                 '202',
            'Custom 3':                 '203',
            'Custom 4':                 '204',
            'Custom 5':                 '205',
        }

        OutputResolutionCmdString = 'w1*{0}RATE\r\n'.format(ValueStateValues[value])
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'w1RATE\r'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '10':  '640x480 (60Hz)',
            '11':  '800x600 (60Hz)',
            '12':  '1024x768 (60Hz)',
            '13':  '1280x768 (60Hz)',
            '14':  '1280x800 (60Hz)',
            '15':  '1280x1024 (60Hz)',
            '16':  '1360x768 (60Hz)',
            '17':  '1366x768 (60Hz)',
            '18':  '1440x900 (60Hz)',
            '19':  '1400x1050 (60Hz)',
            '20':  '1600x900 (60Hz)',
            '21':  '1680x1050 (60Hz)',
            '22':  '1600x1200 (60Hz)',
            '23':  '1920x1200 (60Hz)',
            '24':  '480p (59.94Hz)',
            '25':  '480p (60Hz)',
            '26':  '576p (50Hz)',
            '29':  '720p (25Hz)',
            '30':  '720p (29.97Hz)',
            '31':  '720p (30Hz)',
            '32':  '720p (50Hz)',
            '33':  '720p (59.94Hz)',
            '34':  '720p (60Hz)',
            '38':  '1080p (23.98Hz)',
            '39':  '1080p (24Hz)',
            '40':  '1080p (25Hz)',
            '41':  '1080p (29.97Hz)',
            '42':  '1080p (30Hz)',
            '43':  '1080p (50Hz)',
            '44':  '1080p (59.94Hz)',
            '45':  '1080p (60Hz)',
            '46':  '2048x1080 (2K) (23.98Hz)',
            '47':  '2048x1080 (2K) (24Hz)',
            '48':  '2048x1080 (2K) (25Hz)',
            '49':  '2048x1080 (2K) (29.97Hz)',
            '50':  '2048x1080 (2K) (30Hz)',
            '51':  '2048x1080 (2K) (50Hz)',
            '52':  '2048x1080 (2K) (59.94Hz)',
            '53':  '2048x1080 (2K) (60Hz)',
            '54':  '2048x1200 (60Hz)',
            '55':  '2048x1536 (60Hz)',
            '56':  '2560x1080 (60Hz)',
            '57':  '2560x1440 (60Hz)',
            '58':  '2560x1600 (60Hz)',
            '59':  '3840x2160 (23.98Hz)',
            '60':  '3840x2160 (24Hz)',
            '61':  '3840x2160 (25Hz)',
            '62':  '3840x2160 (29.97Hz)',
            '63':  '3840x2160 (30Hz)',
            '64':  '3840x2160 (50Hz)',
            '65':  '3840x2160 (59.94Hz)',
            '66':  '3840x2160 (60Hz)',
            '69':  '4096x2160 (23.98Hz)',
            '70':  '4096x2160 (24Hz)',
            '71':  '4096x2160 (25Hz)',
            '72':  '4096x2160 (29.97Hz)',
            '73':  '4096x2160 (30Hz)',
            '74':  '4096x2160 (50Hz)',
            '75':  '4096x2160 (59.94Hz)',
            '76':  '4096x2160 (60Hz)',
            '201': 'Custom 1',
            '202': 'Custom 2',
            '203': 'Custom 3',
            '204': 'Custom 4',
            '205': 'Custom 5',
        }

        value = ValueStateValues[str(int(match.group(1).decode()))]
        self.WriteStatus('OutputResolution', value, None)

    def SetPowerSaveMode(self, value, qualifier):

        ValueStateValues = {
            'Lowest':  '1',
            'Lower': '2',
            'Off': '0',
        }

        PowerSaveModeCmdString = 'w{0}PSAV\r'.format(ValueStateValues[value])
        self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        ValueStateValues = {
            '1': 'Lowest',
            '2': 'Lower',
            '0': 'Off',
            '9': 'Over Temp'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def SetProgramInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -18,
            'Max': 24,
        }

        inputNumberValues = {
            '1': [0,1],
            '2': [2,3],
            '3': [4,5],
            '4': [6,7],
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.__SetHelper('ProgramInputGain', 'WG3000{0}*{1}AU\r'.format(inputNumberValues[qualifier['Input']][0], round(value*10)), value, qualifier)
            self.__SetHelper('ProgramInputGain', 'WG3000{0}*{1}AU\r'.format(inputNumberValues[qualifier['Input']][1], round(value*10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramInputGain')

    def UpdateProgramInputGain(self, value, qualifier):

        inputNumberValues = {
            '1': 0,
            '2': 2,
            '3': 4,
            '4': 6,
        }

        inputnumber = inputNumberValues[qualifier['Input']]
        ProgramInputGainCmdString = 'WG3000{0}AU\r'.format(inputNumberValues[qualifier['Input']])
        self.__UpdateHelper('ProgramInputGain', ProgramInputGainCmdString, value, qualifier)

    def __MatchProgramInputGain(self, match, tag):

        qualifier = {}
        InputValue = match.group(1).decode()
        inputNumberValues = {
            '0': '1',
            '1': '1',
            '2': '2',
            '3': '2',
            '4': '3',
            '5': '3',
            '6': '4',
            '7': '4'
        }
        qualifier['Input'] = inputNumberValues[InputValue]
        value = int(match.group(2).decode())/10
        self.WriteStatus('ProgramInputGain', value, qualifier)

    def SetProgramInputMute(self, value, qualifier):

        muteValues = {
            'On': '1',
            'Off': '0'
        }

        inputNumberValues = {
            '1': [0,1],
            '2': [2,3],
            '3': [4,5],
            '4': [6,7],
        }

        if value in muteValues and qualifier['Input'] in inputNumberValues:
            self.__SetHelper('ProgramInputMute',  'WM3000{0}*{1}AU\r'.format(inputNumberValues[qualifier['Input']][0], muteValues[value]), value, qualifier)
            self.__SetHelper('ProgramInputMute',  'WM3000{0}*{1}AU\r'.format(inputNumberValues[qualifier['Input']][1], muteValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramInputMute')

    def UpdateProgramInputMute(self, value, qualifier):

        inputNumberValues = {
            '1': 0,
            '2': 2,
            '3': 4,
            '4': 6,
        }

        inputnumber = inputNumberValues[qualifier['Input']]

        ProgramInputMuteCmdString = 'WM3000{0}AU\r'.format(inputnumber)
        self.__UpdateHelper('ProgramInputMute', ProgramInputMuteCmdString, value, qualifier)

    def __MatchProgramInputMute(self, match, tag):

        muteValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        InputValue = match.group(1).decode()
        inputNumberValues = {
            '0': '1',
            '1': '1',
            '2': '2',
            '3': '2',
            '4': '3',
            '5': '3',
            '6': '4',
            '7': '4'
        }
        qualifier['Input'] = inputNumberValues[InputValue]
        value = muteValues[match.group(2).decode()]
        self.WriteStatus('ProgramInputMute', value, qualifier)

    def UpdateScreenSaverStatus(self, value, qualifier):

        ScreenSaverStatusCmdString = 'wS1SSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', ScreenSaverStatusCmdString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Active Input Detected; Timer not running',
            '1': 'No Active Input; Timer running; Output sync enabled',
            '2': 'No Active Input; Timer expired; Output sync disabled',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'Open':  '0',
            'Close': '1',
        }

        if 1 <= int(qualifier['Port']) <= 7:
            TallyCmdString = 'w{}*{}TALY\r'.format(qualifier['Port'], ValueStateValues[value])
            self.__SetHelper('Tally', TallyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= 7:
            TallyCmdString = 'wTALY\r'
            self.__UpdateHelper('Tally', TallyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTally')

    def __MatchTally(self, match, tag):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Close',
        }

        if tag == 'Unsolicited':
            qualifier = {'Port': match.group(1).decode()}
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Tally', value, qualifier)
        else:
            values = match.group(1).decode().split()
            port = 1
            for i in values:
                self.WriteStatus('Tally', ValueStateValues[i], {'Port': str(port)})
                port += 1

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w28STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Crop':               '1',
            'Alternating Pixels': '2',
            'Crosshatch':         '3',
            'Color Bars':         '4',
            'Grayscale':          '5',
            'Audio Test':         '6',
            'Off':                '0',
        }

        TestPatternCmdString = 'w1*{0}TEST\r'.format(ValueStateValues[value])
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'w1TEST\r'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            '1': 'Crop',
            '2': 'Alternating Pixels',
            '3': 'Crosshatch',
            '4': 'Color Bars',
            '5': 'Grayscale',
            '6': 'Audio Test',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetInputPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetRecallCmdString = '2*{0}.'.format(value)
            self.__SetHelper('InputPresetRecall', InputPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetInputPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetSaveCmdString = '2*{0},'.format(value)
            self.__SetHelper('InputPresetSave', InputPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video Mute': '1',
            'Off': '0',
            'Sync Mute': '2',
        }

        output_ = qualifier['Output']
        if output_ in self.OutputStates:
            VideoMuteCmdString = '{0}*{1}B'.format(self.OutputStates[output_], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            VideoMuteCmdString = '{0}*B'.format(self.OutputStates[qualifier['Output']])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'Video Mute',
            '0': 'Off',
            '2': 'Sync Mute',
        }

        qualifier = {}
        qualifier['Output'] = self.OutputStateValues[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number',
            '06': 'Invalid switch attempt in this mode',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found',
            '33': 'Bad file type for logo',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: '+ match.group(1).decode()])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.CECOutputList.clear()

    def extr_17_17181_2004(self):

        self.OutputStates = {
            '1A': '1',
            '1B': '2',
        }

        self.OutputStateValues = {
            '1': '1A',
            '2': '1B',
        }

        self.AudioFormatStates = {
            'Analog':        '1',
            'LPCM-2Ch':      '2',
            'Multi-Ch':      '3',
            'None':          '0',
        }

        self.AudioFormatStateValues = {
            '1': 'Analog',
            '2': 'LPCM-2Ch',
            '3': 'Multi-Ch',
            '0': 'None',
        }

    def extr_17_17181_DTP3(self):

        self.OutputStates = {
            '1A': '1',
            '1B': '2',
            '1C': '3'
        }

        self.OutputStateValues = {
            '1': '1A',
            '2': '1B',
            '3': '1C'
        }

        self.AudioFormatStates = {
            'Analog':        '1',
            'LPCM-2Ch':      '2',
            'Multi-Ch':      '3',
            'None':          '0',
        }

        self.AudioFormatStateValues = {
            '1': 'Analog',
            '2': 'LPCM-2Ch',
            '3': 'Multi-Ch',
            '0': 'None',
        }

    def extr_17_17181_DIDO(self):

        self.OutputStates = {
            '1A': '1',
            '1B': '2',
            '1C': '3'
        }

        self.OutputStateValues = {
            '1': '1A',
            '2': '1B',
            '3': '1C'
        }

        self.AudioFormatStates = {
            'Analog':        '1',
            'LPCM-2Ch':      '2',
            'Multi-Ch':      '3',
            'LPCM-2Ch Auto': '4',
            'Multi-Ch Auto': '5',
            'None':          '0',
        }

        self.AudioFormatStateValues = {
            '1': 'Analog',
            '2': 'LPCM-2Ch',
            '3': 'Multi-Ch',
            '4': 'LPCM-2Ch Auto',
            '5': 'Multi-Ch Auto',
            '0': 'None',
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
                result = search(regexString, self.__receiveBuffer)
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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