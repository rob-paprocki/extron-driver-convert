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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioFilePlaybackOnce': {'Parameters': ['Priority Level'], 'Status': {}},
            'AudioFilePlaybackRepeat': {'Parameters': ['Priority Level', 'Repeat Rate (Seconds)'], 'Status': {}},
            'AudioFilePlaybackStop': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioStreamStatus': {'Status': {}},
            'ContactInput': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'HDCPSetting': {'Status': {}},
            'Input': {'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputVolume': {'Parameters': ['Input'], 'Status': {}},
            'MicrophoneUsage': {'Status': {}},
            'OutputVolume': {'Status': {}},
            'PowerSaveMode': {'Status': {}},
            'VideoMute': {'Status': {}},
            'VoiceLiftRelay': {'Parameters': ['Relay'], 'Status': {}},
        }

        self.lastInputSignalStatusUpdate = 0
        self.lastVoiceLiftUpdate = 0

        self.EchoDisabled = True
        self.VerboseDisabled = True
       
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'DsG300([0-1][0-9])\*(-?[0-9]{1,3})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(rb'Inf37\*([01])\r\n'), self.__MatchAudioStreamStatus, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(rb'HdcpE([1-6])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(rb'HdcpI([1-6])\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([0-3])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'HdcpS([01])\r\n'), self.__MatchHDCPSetting, None)
            self.AddMatchString(re.compile(b'Chn([1-7])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(rb'Imut(1|8|9|10)\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'Sig([0-2]) ([0-2]) ([0-2]) ([0-2]) ([0-2]) ([0-2])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(rb'DsG4000([0-1])\*(-?[0-9]{1,3})\r\n'), self.__MatchInputVolume, None)
            self.AddMatchString(re.compile(b'Usag([0-9]{5}):([0-9]{2})\r\n'), self.__MatchMicrophoneUsage, None)
            self.AddMatchString(re.compile(b'Vol([0-9]{3})\r\n'), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'Psav([0-4])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(re.compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(rb'Inf34\*([01]) ([01]) [0-3]\r\n'), self.__MatchVoiceLift, None)
            self.AddMatchString(re.compile(rb'Inf34\*Rly1([01]) Rly2([01]) Pair[019][0-9] Ver[0-9.a-z-]+\r\n'), self.__MatchVoiceLift, 'Pro')
            self.AddMatchString(re.compile(b'E([0-3][0-8])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  # Echo Mode for SSH

    def SetVerbose(self, value, qualifier):

        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False
        
    def SetAudioFilePlaybackOnce(self, value, qualifier):

        PriorityLevelStates = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3'
        }

        level = qualifier['Priority Level']

        if level in PriorityLevelStates and 1 <= int(value) <= 20:
            AudioFilePlaybackOnceCmdString = '\x1B1*{0}*0*{1}PLAY\x0D'.format(value, PriorityLevelStates[level])  # First parameter to be set as 1 or 'All'
            self.__SetHelper('AudioFilePlaybackOnce', AudioFilePlaybackOnceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFilePlaybackOnce')

    def SetAudioFilePlaybackRepeat(self, value, qualifier):

        PriorityLevelStates = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3'
        }

        RepeatRateStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '20': '20',
            '30': '30',
            '40': '40',
            '50': '50',
            '60': '60',
            '70': '70',
            '80': '80',
            '90': '90',
            '100': '100'
        }

        level = qualifier['Priority Level']
        rate = qualifier['Repeat Rate (Seconds)']

        if level in PriorityLevelStates and rate in RepeatRateStates and 1 <= int(value) <= 20:
            AudioFilePlaybackRepeatCmdString = '\x1B1*{0}*{1}*{2}PLAY\x0D'.format(value, RepeatRateStates[rate], PriorityLevelStates[level])
            self.__SetHelper('AudioFilePlaybackRepeat', AudioFilePlaybackRepeatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFilePlaybackRepeat')

    def SetAudioFilePlaybackStop(self, value, qualifier):

        AudioFilePlaybackStopCmdString = '\x1B0PLAY\x0D'
        self.__SetHelper('AudioFilePlaybackStop', AudioFilePlaybackStopCmdString, value, qualifier)
        
    def SetAudioGainAttenuation(self, value, qualifier):

        InputStates = {
            '1': ['00', '01'],
            '2': ['02', '03'],
            '3': ['04', '05'],
            '4': ['06', '07'],
            '5': ['08', '09'],
            '6': ['10', '11'],
            '7': ['12', '13']
        }

        ValueConstraints = {
            'Min': -18,
            'Max': 24
        }

        _input = qualifier['Input']

        if _input in InputStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            gain = value * 10
            AudioGainAttenuationCmdString_Left = '\x1Bg300{0}*{1}AU\x0D'.format(InputStates[_input][0], gain)
            AudioGainAttenuationCmdString_Right = '\x1Bg300{0}*{1}AU\x0D'.format(InputStates[_input][1], gain)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString_Left, value, qualifier)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString_Right, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        InputStates = {
            '1': '00',
            '2': '02',
            '3': '04',
            '4': '06',
            '5': '08',
            '6': '10',
            '7': '12'
        }

        _input = qualifier['Input']

        if _input in InputStates:
            AudioGainAttenuationCmdString = '\x1Bg300{0}AU\x0D'.format(InputStates[_input])
            self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def __MatchAudioGainAttenuation(self, match, tag):

        InputStates = {
            '00': '1',
            '01': '1',
            '02': '2',
            '03': '2',
            '04': '3',
            '05': '3',
            '06': '4',
            '07': '4',
            '08': '5',
            '09': '5',
            '10': '6',
            '11': '6',
            '12': '7',
            '13': '7'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        value = int(int(match.group(2).decode()) / 10)
        self.WriteStatus('AudioGainAttenuation', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1Z',
            'Off': '0Z'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def UpdateAudioStreamStatus(self, value, qualifier):

        AudioStreamStatusCmdString = '37I'
        self.__UpdateHelper('AudioStreamStatus', AudioStreamStatusCmdString, value, qualifier)

    def __MatchAudioStreamStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Idle',
            '1': 'Streaming'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioStreamStatus', value, None)

    def UpdateContactInput(self, value, qualifier):

        ContactInputCmdString = '34I'
        self.__UpdateHelper('ContactInput', ContactInputCmdString, value, qualifier)
        
    def __MatchVoiceLift(self, match, tag):

        ContactStates = {
            '0': 'Open',
            '1': 'Closed'
        }

        VoiceLiftRelayStates = {
            '1': 'On',
            '0': 'Off'
        }

        if tag == 'Pro':
            value = VoiceLiftRelayStates[match.group(1).decode()]
            self.WriteStatus('VoiceLiftRelay', value, {'Relay': '1'})

            value = VoiceLiftRelayStates[match.group(2).decode()]
            self.WriteStatus('VoiceLiftRelay', value, {'Relay': '2'})

        else:
            value = VoiceLiftRelayStates[match.group(1).decode()]
            self.WriteStatus('VoiceLiftRelay', value, {'Relay': '1'})

            value = ContactStates[match.group(2).decode()]
            self.WriteStatus('ContactInput', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1X',
            'Off': '0X'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        _input = qualifier['Input']

        if _input in InputStates and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = '\x1BE{0}*{1}HDCP\x0D'.format(InputStates[_input], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        _input = qualifier['Input']

        if 1 <= int(_input) <= 6:
            HDCPInputAuthorizationCmdString = '\x1BE{0}HDCP\x0D'.format(_input)
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        _input = qualifier['Input']

        if 1 <= int(_input) <= 6:
            HDCPInputStatusCmdString = '\x1BI{0}HDCP\x0D'.format(_input)
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        ValueStateValues = {
            '0': 'No Active Video Source Detected',
            '1': 'Video Detected without HDCP',
            '2': 'Video Detected with HDCP'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        Input = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', Input, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = '\x1BOHDCP\x0D'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Active Sink Detected',
            '1': 'Non-HDCP Sink Detected',
            '2': 'HDCP Sink Detected, Output Not Encrypted',
            '3': 'HDCP Sink Detected, Output Encrypted'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetHDCPSetting(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'On': '1'
        }

        if value in ValueStateValues:
            HDCPSettingCmdString = '\x1BS{0}HDCP\x0D'.format(ValueStateValues[value])
            self.__SetHelper('HDCPSetting', HDCPSettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPSetting')

    def UpdateHDCPSetting(self, value, qualifier):

        HDCPSettingCmdString = '\x1BSHDCP\x0D'
        self.__UpdateHelper('HDCPSetting', HDCPSettingCmdString, value, qualifier)

    def __MatchHDCPSetting(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPSetting', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': '1!',
            '2': '2!',
            '3': '3!',
            '4': '4!',
            '5': '5!',
            '6': '6!',
            '7': '7!'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def SetInputMute(self, value, qualifier):

        InputStates = {
            'Active Program': '1',
            'VoiceLift': '8',
            'Aux': '9',
            'HDMI Audio': '10'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        _input = qualifier['Input']

        if _input in InputStates and value in ValueStateValues:
            InputMuteCmdString = '\x1B{0}*{1}IMUT\x0D'.format(InputStates[_input], ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        InputValues = {
            'Active Program': '1',
            'VoiceLift': '8',
            'Aux': '9',
            'HDMI Audio': '10'
        }

        _input = qualifier['Input']

        if _input in InputValues:
            InputMuteCmdString = '\x1B{0}IMUT\x0D'.format(InputValues[_input])
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        InputStates = {
            '1': 'Active Program',
            '8': 'VoiceLift',
            '9': 'Aux',
            '10': 'HDMI Audio'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        Input = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, {'Input': Input})

    def UpdateInputSignalStatus(self, value, qualifier):

        _input = int(qualifier['Input'])

        if 1 <= _input <= 6:
            self.__UpdateHelper('InputSignalStatus', '\x1BLS\x0D', value, qualifier)           
        else:
            self.Discard('Device Is Busy for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusStateNames = {
            '0': 'Not Active',
            '1': 'Active',
            '2': 'Unknown'
        }

        for i in range(1, 7):
            self.WriteStatus('InputSignalStatus', InputSignalStatusStateNames[match.group(i).decode()], {'Input': str(i)})

    def SetInputVolume(self, value, qualifier):

        InputStates = {
            'Aux': '1',
            'VoiceLift': '0'
        }

        ValueConstraints = {
            'Min': -18,
            'Max': 24
        }

        _input = qualifier['Input']

        if _input in InputStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volume = value * 10
            InputVolumeCmdString = '\x1Bg4000{0}*{1}AU\x0D'.format(InputStates[_input], volume)
            self.__SetHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputVolume')

    def UpdateInputVolume(self, value, qualifier):

        InputStates = {
            'Aux': '1',
            'VoiceLift': '0'
        }

        _input = qualifier['Input']

        if _input in InputStates:
            InputVolumeCmdString = '\x1Bg4000{0}AU\x0D'.format(InputStates[_input])
            self.__UpdateHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputVolume')

    def __MatchInputVolume(self, match, tag):

        InputStates = {
            '1': 'Aux',
            '0': 'VoiceLift'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        value = int(int(match.group(2).decode()) / 10)
        self.WriteStatus('InputVolume', value, qualifier)

    def UpdateMicrophoneUsage(self, value, qualifier):

        MicrophoneUsageCmdString = '\x1BUSAG\r\n'
        self.__UpdateHelper('MicrophoneUsage', MicrophoneUsageCmdString, value, qualifier)

    def __MatchMicrophoneUsage(self, match, tag):

        hours = int(match.group(1).decode())
        minutes = int(match.group(2).decode())
        value = '{0}:{1}'.format(hours, minutes)

        self.WriteStatus('MicrophoneUsage', value, None)

    def SetOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputVolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputVolumeCmdString = 'V'
        self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OutputVolume', value, None)

    def SetPowerSaveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Mode 3': '3',
            'Mode 4': '4',
            'Off': '0'
        }

        if value in ValueStateValues:
            PowerSaveModeCmdString = '\x1B{0}PSAV\x0D'.format(ValueStateValues[value])
            self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerSaveMode')

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = '\x1BPSAV\x0D'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        ValueStateValues = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3',
            '4': 'Mode 4',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1B',
            'Off': '0B'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def UpdateVoiceLiftRelay(self, value, qualifier):

        if 1 <= int(qualifier['Relay']) <= 2:
            self.UpdateContactInput(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVoiceLiftRelay')

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
            '01': 'Invalid input channel number',          
            '10': 'Invalid command',
            '12': 'Invalid port number',
            '13': 'Invalid parameter(out of range)',   
            '14': 'Illegal command for this configuration',
            '17': 'System time out', 
            '18': 'System/command timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad Filename/File not found',
            '34': 'Key not found'
        }
            
        value = match.group(1).decode()

        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.lastInputSignalStatusUpdate = 0
        self.lastVoiceLiftUpdate = 0

        self.EchoDisabled = True
        self.VerboseDisabled = True
        
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
