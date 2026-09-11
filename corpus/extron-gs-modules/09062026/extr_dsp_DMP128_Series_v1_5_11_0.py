from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'DMP 128': self.extr_25_5_128,
            'DMP 128CP AT': self.extr_25_5_128PAT,
            'DMP 128C': self.extr_25_5_128,
            'DMP 128C AT': self.extr_25_5_128AT,
            'DMP 128 AT': self.extr_25_5_128AT,
            'DMP 128CP': self.extr_25_5_128P,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoHangup': {'Status': {}},
            'CallerID': {'Parameters': ['Field'], 'Status': {}},
            'CallStatus': {'Status': {}},
            'DialDTMF': {'Status': {}},
            'DigitalIOMode': {'Parameters': ['Port'], 'Status': {}},
            'DigitalIOState': {'Parameters': ['Port'], 'Status': {}},
            'DTMFToneVolume': {'Status': {}},
            'ExpansionBusMixpointGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'ExpansionBusMixpointMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'GroupBassInputFilter': {'Parameters': ['Group'], 'Status': {}},
            'GroupBassVirtualReturnFilter': {'Parameters': ['Group'], 'Status': {}},
            'GroupMixpointGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupMute': {'Parameters': ['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters': ['Group'], 'Status': {}},
            'GroupPostmixerTrim': {'Parameters': ['Group'], 'Status': {}},
            'GroupPremixerGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupTrebleInputFilter': {'Parameters': ['Group'], 'Status': {}},
            'GroupTrebleVirtualReturnFilter': {'Parameters': ['Group'], 'Status': {}},
            'GroupVirtualReturnGain': {'Parameters': ['Group'], 'Status': {}},
            'Hook': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'MixpointGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MixpointMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'OutputAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'OutputPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'PartNumber': {'Status': {}},
            'PhoneErrorStatus': {'Status': {}},
            'PremixerGain': {'Parameters': ['Input'], 'Status': {}},
            'PremixerMute': {'Parameters': ['Input'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'VirtualReturnGain': {'Parameters': ['Input'], 'Status': {}},
            'VirtualReturnMute': {'Parameters': ['Input'], 'Status': {}},
        }

        self.GroupFunction = {}
        self.DigitalIOModePorts = []
        self.DigitalIOStatePorts = []
        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.IncomingCallTimerEnabled = False
        self.ReDialString = ''
        self.devicePassword = None
        self.TerminateEnabled = False

        self.ExpansionBusOutputStateValues = {
            '1': '00',
            '2': '01',
            '3': '02',
            '4': '03',
            '5': '04',
            '6': '05',
            '7': '06',
            '8': '07',
            'V. Send A': '09',
            'V. Send B': '10',
            'V. Send C': '11',
            'V. Send D': '12',
            'V. Send E': '13',
            'V. Send F': '14',
            'V. Send G': '15',
            'V. Send H': '16',
        }

        self.ExpansionBusOutputStateNames = {
            '00': '1',
            '01': '2',
            '02': '3',
            '03': '4',
            '04': '5',
            '05': '6',
            '06': '7',
            '07': '8',
            '09': 'V. Send A',
            '10': 'V. Send B',
            '11': 'V. Send C',
            '12': 'V. Send D',
            '13': 'V. Send E',
            '14': 'V. Send F',
            '15': 'V. Send G',
            '16': 'V. Send H',
        }
        self.MixpointOutputStateValues = {
            '1': '00',
            '2': '01',
            '3': '02',
            '4': '03',
            '5': '04',
            '6': '05',
            '7': '06',
            '8': '07',
            'V. Send A': '09',
            'V. Send B': '10',
            'V. Send C': '11',
            'V. Send D': '12',
            'V. Send E': '13',
            'V. Send F': '14',
            'V. Send G': '15',
            'V. Send H': '16',
            'Exp. 1': '17',
            'Exp. 2': '18',
            'Exp. 3': '19',
            'Exp. 4': '20',
            'Exp. 5': '21',
            'Exp. 6': '22',
            'Exp. 7': '23',
            'Exp. 8': '24'
        }
        self.MixpointOutputStateNames = {
            '00': '1',
            '01': '2',
            '02': '3',
            '03': '4',
            '04': '5',
            '05': '6',
            '06': '7',
            '07': '8',
            '09': 'V. Send A',
            '10': 'V. Send B',
            '11': 'V. Send C',
            '12': 'V. Send D',
            '13': 'V. Send E',
            '14': 'V. Send F',
            '15': 'V. Send G',
            '16': 'V. Send H',
            '17': 'Exp. 1',
            '18': 'Exp. 2',
            '19': 'Exp. 3',
            '20': 'Exp. 4',
            '21': 'Exp. 5',
            '22': 'Exp. 6',
            '23': 'Exp. 7',
            '24': 'Exp. 8'
        }

        self.VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.LevelTypes = {
            'GroupBassInputFilter': {'Min': -24, 'Max': 24},
            'GroupBassVirtualReturnFilter': {'Min': -24, 'Max': 24},
            'GroupTrebleInputFilter': {'Min': -24, 'Max': 24},
            'GroupTrebleVirtualReturnFilter': {'Min': -24, 'Max': 24},
            'GroupMixpointGain': {'Min': -35, 'Max': 25},
            'GroupOutputAttenuation': {'Min': -100, 'Max': 0},
            'GroupPostmixerTrim': {'Min': -12, 'Max': 12},
            'GroupPremixerGain': {'Min': -100, 'Max': 12},
            'GroupVirtualReturnGain': {'Min': -100, 'Max': 12},
            'InputGain': {'Min': -18, 'Max': 80},
            'MixpointGain': {'Min': -35, 'Max': 25},
            'OutputAttenuation': {'Min': -100, 'Max': 0},
            'OutputPostmixerTrim': {'Min': -12, 'Max': 12},
            'PremixerGain': {'Min': -100, 'Max': 12},
            'VirtualReturnGain': {'Min': -100, 'Max': 12},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(Pno60-(1211|1178|1179)-(01|10))\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(compile(b'((?:Cpn[0-1]\r\n){1,20})Inf(01|02)\*DMP 128'), self.__MatchDigitalIO, None)
            self.AddMatchString(compile(b'PhonAH([01])\r\n'), self.__MatchAutoHangup, None)
            self.AddMatchString(compile(b'PhonNAME=([a-zA-Z0-9|\s]+)\r\n'), self.__MatchCallerID, 'Name')
            self.AddMatchString(compile(b'PhonNMBR=([0-9*#+]{1,12})\r\n'), self.__MatchCallerID, 'Number')
            self.AddMatchString(compile(b'PhonDATE=([0-9]{1,4})\r\n'), self.__MatchCallerID, 'Date')
            self.AddMatchString(compile(b'PhonTIME=([0-9]{1,4})\r\n'), self.__MatchCallerID, 'Time')
            self.AddMatchString(compile(b'Phon(Dial_Tone|Ringing_Tone|Busy_Tone|Line_Intr|RING|Dialing|DialDone|DialDigit)\r\n'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'PhonDG([0-9]{1,4})\r\n'), self.__MatchDTMFToneVolume, None)
            self.AddMatchString(compile(b'GrpmD([0-9]{2})\*([-+]0[0-9]{4})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(compile(b'Phon(Sts00|Sts13|Sts20|OffHook|OnHook|StsOnHook|StsOffHook)\r\n'), self.__MatchHook, None)
            self.AddMatchString(compile(b'DsG(400[0-9]{2})\*(0[0-9]{4})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'DsM(400[0-9]{2})\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'DsG2([0-9]{2})([0-9]{2})\*(0[0-9]{4})\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(compile(b'DsM2([0-9]{2})([0-9]{2})\*([01])\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(compile(b'DsM(6000[0-8])\*([01])\r\n'), self.__MatchOutputMute, None)
            self.AddMatchString(compile(b'DsG(6000[0-8])\*(0[0-9]{4})\r\n'), self.__MatchOutputAttenuation, None)
            self.AddMatchString(compile(b'DsG(6010[0-8])\*([0-9 -]{1,5})\r\n'), self.__MatchOutputPostmixerTrim, None)
            self.AddMatchString(compile(b'Phon(Error|_Non_Voice|OK)\r\n'), self.__MatchPhoneErrorStatus, None)
            self.AddMatchString(compile(b'DsG(401[0-9]{2})\*(0[0-9]{4})\r\n'), self.__MatchPremixerGain, None)
            self.AddMatchString(compile(b'DsM(401[0-9]{2})\*([01])\r\n'), self.__MatchPremixerMute, None)
            self.AddMatchString(compile(b'DsG(5000[0-7])\*(0[0-9]{4})\r\n'), self.__MatchVirtualReturnGain, None)
            self.AddMatchString(compile(b'DsM(5000[0-7])\*([01])\r\n'), self.__MatchVirtualReturnMute, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'E([0-9]{2})\r\n'), self.__MatchError, None)

            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

        self.IncomingCallTimer = Wait(8, self.IncomingCallCheck)
        self.IncomingCallTimer.Cancel()

    def UpdatePartNumber(self, value, qualifier):

        cmdString = 'n'
        self.__UpdateHelper('PartNumber', cmdString, None, None)

    def __MatchPartNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PartNumber', value, None)

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
        else:
            if self.devicePassword is not None:
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Password')
        self.Authenticated = 'None'

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAutoHangup(self, value, qualifier):

        AutoHangupStateValues = {
            'Enabled': '1',
            'Disabled': '0'
        }

        commandString = 'wAH{0},PHON\r\n'.format(AutoHangupStateValues[value])
        self.__SetHelper('AutoHangup', commandString, value, qualifier)

    def UpdateAutoHangup(self, value, qualifier):

        commandString = 'wAH,PHON\r\n'
        self.__UpdateHelper('AutoHangup', commandString, value, qualifier)

    def __MatchAutoHangup(self, match, tag):

        AutoHangupStateNames = {
            '1': 'Enabled',
            '0': 'Disabled'
        }

        value = AutoHangupStateNames[match.group(1).decode()]
        self.WriteStatus('AutoHangup', value, None)

    def __MatchCallerID(self, match, tag):

        qualifier = {'Field': tag}
        value = match.group(1).decode()

        if tag == 'Date':
            value = '{0:02d}/{1:02d}'.format(int(value[:2]), int(value[2:]))
        elif tag == 'Time':
            period = 'AM'
            hh = int(value[:2])
            mm = int(value[2:])
            if hh > 12:
                hh = hh - 12
                period = 'PM'
            value = '{0}:{1:02d} {2}'.format(hh, mm, period)
        self.WriteStatus('CallerID', value, qualifier)

    def ClearCallerId(self):

        fields = ['Name', 'Number', 'Date', 'Time']
        for field in fields:
            self.WriteStatus('CallerID', '', {'Field': field})

    def __MatchCallStatus(self, match, tag):

        CallStatusStateNames = {
            'Dial_Tone': 'Dial Tone',
            'Ringing_Tone': 'Connected',
            'Busy_Tone': 'Busy',
            'RING': 'Incoming',
            'Line_Intr': 'Terminated',
            'Dialing': 'Dialing',
            'DialDone': 'Connected',
            'DialDigit': 'Connected',
        }
        value = CallStatusStateNames[match.group(1).decode()]

        if value == 'Incoming':
            self.IncomingCallTimer.Restart()
        elif value == 'Terminated':
            self.ClearCallerId()
        self.WriteStatus('CallStatus', value, None)

    def IncomingCallCheck(self):
        HookStatus = self.ReadStatus('Hook', None)
        if HookStatus == 'On':
            self.WriteStatus('CallStatus', 'Idle', None)
            self.IncomingCallTimerEnabled = False

    def SetExpansionBusMixpointGain(self, value, qualifier):

        Input, Output = qualifier['Input'], qualifier['Output']
        if self.__CheckValidLevelValue('MixpointGain', value):
            inputValue = self.ExpansionBusInputStateValues[Input]
            outputValue = self.ExpansionBusOutputStateValues[Output]
            level = round(value * 10) + 2048
            commandString = 'wG2{0}{1}*{2:05d}AU\r\n'.format(inputValue, outputValue, level)
            self.__SetHelper('ExpansionBusMixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExpansionBusMixpointGain')

    def UpdateExpansionBusMixpointGain(self, value, qualifier):

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = self.ExpansionBusInputStateValues[Input]
        outputValue = self.ExpansionBusOutputStateValues[Output]
        commandString = 'wG2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('ExpansionBusMixpointGain', commandString, value, qualifier)

    def SetExpansionBusMixpointMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = self.ExpansionBusInputStateValues[Input]
        outputValue = self.ExpansionBusOutputStateValues[Output]
        ExpansionBusMixpointMuteCmdString = 'wM2{0}{1}*{2}AU\r\n'.format(inputValue, outputValue, ValueStateValues[value])
        self.__SetHelper('ExpansionBusMixpointMute', ExpansionBusMixpointMuteCmdString, value, qualifier)

    def UpdateExpansionBusMixpointMute(self, value, qualifier):

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = self.ExpansionBusInputStateValues[Input]
        outputValue = self.ExpansionBusOutputStateValues[Output]
        ExpansionBusMixpointMuteCmdString = 'wM2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('ExpansionBusMixpointMute', ExpansionBusMixpointMuteCmdString, value, qualifier)

    def SetDialDTMF(self, value, qualifier):

        DialDTMFcmdString = 'WS{0},PHON\r\n'.format(value)
        self.__SetHelper('DialDTMF', DialDTMFcmdString, value, qualifier)

    def UpdateDigitalIOMode(self, value, qualifier):

        if qualifier['Port'] not in self.DigitalIOModePorts:
            self.DigitalIOModePorts.append(qualifier['Port'])

        cmdString = ''
        for port in self.DigitalIOModePorts:
            cmdString = '{0}{1}['.format(cmdString, port)

        cmdString = '{0}2I'.format(cmdString)
        self.__UpdateHelper('DigitalIOMode', cmdString, value, qualifier)

    def __MatchDigitalIO(self, match, tag):

        DigitalIOModeNames = {
            '0': 'Input',
            '1': 'Output'
        }
        DigitalIOStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        resStates = match.group(1).decode().splitlines()

        if match.group(2).decode() == '02':
            if len(resStates) == len(self.DigitalIOModePorts):
                for i in range(0, len(self.DigitalIOModePorts)):
                    qualifier = {'Port': self.DigitalIOModePorts[i]}
                    self.WriteStatus('DigitalIOMode', DigitalIOModeNames[resStates[i][-1:]], qualifier)

        elif match.group(2).decode() == '01':
            if len(resStates) == len(self.DigitalIOStatePorts):
                for i in range(0, len(self.DigitalIOStatePorts)):
                    qualifier = {'Port': self.DigitalIOStatePorts[i]}
                    self.WriteStatus('DigitalIOState', DigitalIOStateNames[resStates[i][-1:]], qualifier)
        else:
            self.Error(['Incomplete Digital IO Response'])

    def UpdateDigitalIOState(self, value, qualifier):

        if qualifier['Port'] not in self.DigitalIOStatePorts:
            self.DigitalIOStatePorts.append(qualifier['Port'])

        cmdString = ''

        for port in self.DigitalIOStatePorts:
            cmdString = '{0}{1}]'.format(cmdString, port)

        cmdString = '{0}1I'.format(cmdString)
        self.__UpdateHelper('DigitalIOState', cmdString, value, qualifier)

    def SetDTMFToneVolume(self, value, qualifier):

        valueInt = int(value) * 10
        commandString = 'wDG{0:04d},PHON\r\n'.format(valueInt)
        self.__SetHelper('DTMFToneVolume', commandString, value, qualifier)

    def UpdateDTMFToneVolume(self, value, qualifier):

        commandString = 'wDG,PHON\r\n'
        self.__UpdateHelper('DTMFToneVolume', commandString, value, qualifier)

    def __MatchDTMFToneVolume(self, match, tag):

        value = int(int(match.group(1).decode()) / 10)
        self.WriteStatus('DTMFToneVolume', value, None)

    def SetGroupBassInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupBassInputFilter', value):
            level = round(value * 10)
            GroupBassInputFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupBassInputFilter'
            self.__SetHelper('GroupBassInputFilter', GroupBassInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupBassInputFilter')

    def UpdateGroupBassInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            GroupBassInputFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupBassInputFilter'
            self.__UpdateHelper('GroupBassInputFilter', GroupBassInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupBassInputFilter')

    def SetGroupBassVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupBassVirtualReturnFilter', value):
            level = round(value * 10)
            GroupBassVirtualReturnFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupBassVirtualReturnFilter'
            self.__SetHelper('GroupBassVirtualReturnFilter', GroupBassVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupBassVirtualReturnFilter')

    def UpdateGroupBassVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            GroupBassVirtualReturnFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupBassVirtualReturnFilter'
            self.__UpdateHelper('GroupBassVirtualReturnFilter', GroupBassVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupBassVirtualReturnFilter')

    def SetGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupMixpointGain', value):
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__SetHelper('GroupMixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMixpointGain')

    def UpdateGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__UpdateHelper('GroupMixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMixpointGain')

    def SetGroupMute(self, value, qualifier):

        GroupMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}*{1}grpm\r\n'.format(group, GroupMuteStateValues[value])
            self.GroupFunction[group] = 'GroupMute'
            self.__SetHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMute'
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupOutputAttenuation', value):
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)

    def SetGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupPostmixerTrim', value):
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupPostmixerTrim'
            self.__SetHelper('GroupPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupPostmixerTrim')

    def UpdateGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupPostmixerTrim'
            self.__UpdateHelper('GroupPostmixerTrim', commandString, value, qualifier)

    def SetGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupPremixerGain', value):
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupPremixerGain'
            self.__SetHelper('GroupPremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupPremixerGain')

    def UpdateGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupPremixerGain'
            self.__UpdateHelper('GroupPremixerGain', commandString, value, qualifier)

    def SetGroupTrebleInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupTrebleInputFilter', value):
            level = round(value * 10)
            GroupTrebleInputFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupTrebleInputFilter'
            self.__SetHelper('GroupTrebleInputFilter', GroupTrebleInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTrebleInputFilter')

    def UpdateGroupTrebleInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            GroupTrebleInputFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupTrebleInputFilter'
            self.__UpdateHelper('GroupTrebleInputFilter', GroupTrebleInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupTrebleInputFilter')

    def SetGroupTrebleVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupTrebleVirtualReturnFilter', value):
            level = round(value * 10)
            GroupTrebleVirtualReturnFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupTrebleVirtualReturnFilter'
            self.__SetHelper('GroupTrebleVirtualReturnFilter', GroupTrebleVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTrebleVirtualReturnFilter')

    def UpdateGroupTrebleVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            GroupTrebleVirtualReturnFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupTrebleVirtualReturnFilter'
            self.__UpdateHelper('GroupTrebleVirtualReturnFilter', GroupTrebleVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupTrebleVirtualReturnFilter')

    def SetGroupVirtualReturnGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupVirtualReturnGain', value):
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupVirtualReturnGain'
            self.__SetHelper('GroupVirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupVirtualReturnGain')

    def UpdateGroupVirtualReturnGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupVirtualReturnGain'
            self.__UpdateHelper('GroupVirtualReturnGain', commandString, value, qualifier)

    def __MatchGroup(self, match, tag):

        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                GroupMuteStateNames = {
                    '1': 'On',
                    '0': 'Off'
                }
                qualifier = {'Group': group}
                value = match.group(2).decode()[-1]
                self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
            elif command in ['GroupPremixerGain', 'GroupOutputAttenuation',
                             'GroupMixpointGain', 'GroupPostmixerTrim',
                             'GroupVirtualReturnGain', 'GroupBassInputFilter',
                             'GroupBassVirtualReturnFilter', 'GroupTrebleInputFilter',
                             'GroupTrebleVirtualReturnFilter']:
                qualifier = {'Group': group}
                value = int(match.group(2)) / 10
                self.WriteStatus(command, value, qualifier)

    def SetHook(self, value, qualifier):

        if value == 'Off':
            HookCmdString = 'WOFFHOOK,PHON\r\n'
            self.__SetHelper('Hook', HookCmdString, value, qualifier)
            self.IncomingCallTimer.Cancel()
        elif value == 'On':
            HookCmdString = 'WONHOOK,PHON\r\n'
            self.__SetHelper('Hook', HookCmdString, value, qualifier)
        elif value == 'Flash':
            cmdString = 'WF,PHON\r\n'
            self.__SetHelper('Hook', cmdString, value, qualifier)
        elif value == 'Dial':
            number = qualifier['Number']
            if number:
                HookCmdString = 'WD{0},PHON\r\n'.format(number)
                self.__SetHelper('Hook', HookCmdString, value, qualifier)
                self.ReDialString = number
            else:
                self.ReDialString = ''
        elif value == 'Redial':
            if self.ReDialString:
                HookCmdString = 'WD{0},PHON\r\n'.format(self.ReDialString)
                self.__SetHelper('Hook', HookCmdString, value, qualifier)
            else:
                self.Error(['Invalid Command for SetHook Redial'])
        elif value == 'Clear Redial':
            if self.ReDialString:
                self.ReDialString = ''

    def UpdateHook(self, value, qualifier):
        commandString = 'WO,PHON\r'
        self.__UpdateHelper('Hook', commandString, value, qualifier)

    def __MatchHook(self, match, tag):

        HookStateNames = {
            'Sts00': 'On',
            'Sts13': 'Off',
            'OffHook': 'Off',
            'OnHook': 'On',
            'Sts20': 'On'
        }
        value = HookStateNames[match.group(1).decode()]

        self.WriteStatus('Hook', value, None)
        if value == 'On':
            CallStatus = self.ReadStatus('CallStatus', None)
            if CallStatus != 'Incoming':
                self.WriteStatus('CallStatus', 'Idle', None)
                self.ClearCallerId()
        elif value == 'Off':
            CallStatus = self.ReadStatus('CallStatus', None)
            if CallStatus == 'Incoming':
                self.WriteStatus('CallStatus', 'Connected', None)

    def SetInputGain(self, value, qualifier):

        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs and self.__CheckValidLevelValue('InputGain', value):
            level = round(value * 10) + 2048
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 39999, level)
            self.__SetHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs:
            commandString = 'wG{0}AU\r\n'.format(channel + 39999)
            self.__UpdateHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        channel = str(int(match.group(1)) - 39999)
        if channel == '13':
            channel = 'Telephone Rx'
        qualifier = {'Input': channel}
        value = (int(match.group(2)) - 2048) / 10
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 39999, MuteStateValues[value])
            self.__SetHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs:
            commandString = 'wM{0}*AU\r\n'.format(channel + 39999)
            self.__UpdateHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        channel = str(int(match.group(1)) - 39999)
        if channel == '13':
            channel = 'Telephone Rx'
        qualifier = {'Input': channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetMixpointGain(self, value, qualifier):

        Input, Output = qualifier['Input'], qualifier['Output']
        if self.__CheckValidLevelValue('MixpointGain', value):
            inputValue = self.MixpointInputStateValues[Input]
            outputValue = self.MixpointOutputStateValues[Output]
            level = round(value * 10) + 2048
            commandString = 'wG2{0}{1}*{2:05d}AU\r\n'.format(inputValue, outputValue, level)
            self.__SetHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')

    def UpdateMixpointGain(self, value, qualifier):

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = self.MixpointInputStateValues[Input]
        outputValue = self.MixpointOutputStateValues[Output]
        commandString = 'wG2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('MixpointGain', commandString, value, qualifier)

    def __MatchMixpointGain(self, match, tag):

        if 0 <= int(match.group(1).decode()) <= 20:
            Input = self.MixpointInputStateNames[match.group(1).decode()]
            Output = self.MixpointOutputStateNames[match.group(2).decode()]
            value = (int(match.group(3)) - 2048) / 10
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('MixpointGain', value, qualifier)
        else:
            Input = self.ExpansionBusInputStateNames[match.group(1).decode()]
            Output = self.ExpansionBusOutputStateNames[match.group(2).decode()]
            value = (int(match.group(3)) - 2048) / 10
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('ExpansionBusMixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = self.MixpointInputStateValues[Input]
        outputValue = self.MixpointOutputStateValues[Output]
        commandString = 'wM2{0}{1}*{2}AU\r\n'.format(inputValue, outputValue, MuteStateValues[value])
        self.__SetHelper('MixpointMute', commandString, value, qualifier)

    def UpdateMixpointMute(self, value, qualifier):

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = self.MixpointInputStateValues[Input]
        outputValue = self.MixpointOutputStateValues[Output]
        commandString = 'wM2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('MixpointMute', commandString, value, qualifier)

    def __MatchMixpointMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        if 0 <= int(match.group(1).decode()) <= 20:
            Input = self.MixpointInputStateNames[match.group(1).decode()]
            Output = self.MixpointOutputStateNames[match.group(2).decode()]
            value = MuteStateNames[match.group(3).decode()]
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('MixpointMute', value, qualifier)
        else:
            Input = self.ExpansionBusInputStateNames[match.group(1).decode()]
            Output = self.ExpansionBusOutputStateNames[match.group(2).decode()]
            value = MuteStateNames[match.group(3).decode()]
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('ExpansionBusMixpointMute', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        if qualifier['Output'] == 'Telephone Tx':
            channel = 9
        else:
            channel = int(qualifier['Output'])
        if 1 <= channel <= self.MaxOutputs:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 59999, MuteStateValues[value])
            self.__SetHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        if qualifier['Output'] == 'Telephone Tx':
            channel = 9
        else:
            channel = int(qualifier['Output'])
        if 1 <= channel <= self.MaxOutputs:
            commandString = 'wM{0}*AU\r\n'.format(channel + 59999)
            self.__UpdateHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        channel = str(int(match.group(1)) - 59999)
        if channel == '9':
            channel = 'Telephone Tx'
        qualifier = {'Output': channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetOutputPostmixerTrim(self, value, qualifier):

        channel = qualifier['Output']
        if 0 < int(channel) < 9 and self.__CheckValidLevelValue('OutputPostmixerTrim', value):
            level = round(value * 10) + 2048
            ChannelValue = int(channel) + 60099
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(ChannelValue, level)
            self.__SetHelper('OutputPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputPostmixerTrim')

    def UpdateOutputPostmixerTrim(self, value, qualifier):

        channel = qualifier['Output']
        if 0 < int(channel) < 9:
            ChannelValue = int(channel) + 60099
            commandString = 'wG{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('OutputPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputPostmixerTrim')

    def __MatchOutputPostmixerTrim(self, match, tag):

        channel = str(int(match.group(1)) - 60099)
        qualifier = {'Output': channel}
        value = (int(match.group(2)) - 2048) / 10
        self.WriteStatus('OutputPostmixerTrim', value, qualifier)

    def SetOutputAttenuation(self, value, qualifier):

        if qualifier['Output'] == 'Telephone Tx':
            channel = 9
        else:
            channel = int(qualifier['Output'])
        if 1 <= channel <= self.MaxOutputs and self.__CheckValidLevelValue('OutputAttenuation', value):
            level = round(value * 10) + 2048
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 59999, level)
            self.__SetHelper('OutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAttenuation')

    def UpdateOutputAttenuation(self, value, qualifier):

        if qualifier['Output'] == 'Telephone Tx':
            channel = 9
        else:
            channel = int(qualifier['Output'])
        if 1 <= channel <= self.MaxOutputs:
            commandString = 'wG{0}AU\r\n'.format(channel + 59999)
            self.__UpdateHelper('OutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAttenuation')

    def __MatchOutputAttenuation(self, match, tag):

        channel = str(int(match.group(1)) - 59999)
        if channel == '9':
            channel = 'Telephone Tx'
        qualifier = {'Output': channel}
        value = (int(match.group(2)) - 2048) / 10
        self.WriteStatus('OutputAttenuation', value, qualifier)

    def __MatchPhoneErrorStatus(self, match, tag):

        PhoneErrorStatusStateNames = {
            'Error': 'Unrecognized phone command',
            'Error_Non_Voice': 'Phone was not initialized properly',
            'OK': 'Normal'
        }
        value = PhoneErrorStatusStateNames[match.group(1).decode()]
        self.WriteStatus('PhoneErrorStatus', value, None)

    def SetPremixerGain(self, value, qualifier):

        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs and self.__CheckValidLevelValue('PremixerGain', value):
            level = round(value * 10) + 2048
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 40099, level)
            self.__SetHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerGain')

    def UpdatePremixerGain(self, value, qualifier):

        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs:
            commandString = 'wG{0}AU\r\n'.format(channel + 40099)
            self.__UpdateHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerGain')

    def __MatchPremixerGain(self, match, tag):

        channel = str(int(match.group(1)) - 40099)
        if channel == '13':
            channel = 'Telephone Rx'
        qualifier = {'Input': channel}
        value = (int(match.group(2)) - 2048) / 10
        self.WriteStatus('PremixerGain', value, qualifier)

    def SetPremixerMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 40099, MuteStateValues[value])
            self.__SetHelper('PremixerMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerMute')

    def UpdatePremixerMute(self, value, qualifier):

        if qualifier['Input'] == 'Telephone Rx':
            channel = 13
        else:
            channel = int(qualifier['Input'])
        if 1 <= channel <= self.MaxInputs:
            commandString = 'wM{0}*AU\r\n'.format(channel + 40099)
            self.__UpdateHelper('PremixerMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerMute')

    def __MatchPremixerMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        channel = str(int(match.group(1)) - 40099)
        if channel == '13':
            channel = 'Telephone Rx'
        qualifier = {'Input': channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('PremixerMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) <= 32:
            commandString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetVirtualReturnGain(self, value, qualifier):

        channel = qualifier['Input']
        if channel in self.VirtualChannels and self.__CheckValidLevelValue('VirtualReturnGain', value):
            level = round(value * 10) + 2048
            ChannelValue = ord(channel) + 49935
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(ChannelValue, level)
            self.__SetHelper('VirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnGain')

    def UpdateVirtualReturnGain(self, value, qualifier):

        channel = qualifier['Input']
        if channel in self.VirtualChannels:
            ChannelValue = ord(channel) + 49935
            commandString = 'wG{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('VirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualReturnGain')

    def __MatchVirtualReturnGain(self, match, tag):

        channel = chr(int(match.group(1)) - 49935)
        qualifier = {'Input': channel}
        value = (int(match.group(2)) - 2048) / 10
        self.WriteStatus('VirtualReturnGain', value, qualifier)

    def SetVirtualReturnMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        channel = qualifier['Input']
        if channel in self.VirtualChannels:
            ChannelValue = ord(channel) + 49935
            commandString = 'wM{0}*{1}AU\r\n'.format(ChannelValue, MuteStateValues[value])
            self.__SetHelper('VirtualReturnMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnMute')

    def UpdateVirtualReturnMute(self, value, qualifier):

        channel = qualifier['Input']
        if channel in self.VirtualChannels:
            ChannelValue = ord(channel) + 49935
            commandString = 'wM{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('VirtualReturnMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualReturnMute')

    def __MatchVirtualReturnMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        channel = chr(int(match.group(1)) - 49935)
        qualifier = {'Input': channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('VirtualReturnMute', value, qualifier)

    def __CheckValidLevelValue(self, command, value):
        return self.LevelTypes[command]['Min'] <= value <= self.LevelTypes[command]['Max']

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
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

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):

        DeviceErrorCodes = {
            '11': 'Invalid preset',
            '12': 'Invalid port number',
            '13': 'Invalid parameter (number is out of range)',
            '14': 'Not valid for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device is not present',
            '26': 'Maximum connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
        }

        self.Error([DeviceErrorCodes.get(match.group(1).decode(), 'Unrecognized error code: {0}'.format(match.group(0).decode()))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0
        self.VerboseDisabled = True

    def extr_25_5_128(self):
        self.MaxInputs = 12
        self.MaxOutputs = 8
        self.ExpansionBusInputStateValues = {
            '1': '21', '2': '22', '3': '23', '4': '24', '5': '25', '6': '26',
            '7': '27', '8': '28', '9': '29', '10': '30', '11': '31', '12': '32',
            '13': '33', '14': '34', '15': '35', '16': '36'
        }
        self.ExpansionBusInputStateNames = {
            '21': '1', '22': '2', '23': '3', '24': '4', '25': '5', '26': '6',
            '27': '7', '28': '8', '29': '9', '30': '10', '31': '11', '32': '12',
            '33': '13', '34': '14', '35': '15', '36': '16'
        }
        self.MixpointInputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03', '5': '04', '6': '05',
            '7': '06', '8': '07', '9': '08', '10': '09', '11': '10', '12': '11',
            'V. Return A': '13', 'V. Return B': '14', 'V. Return C': '15',
            'V. Return D': '16', 'V. Return E': '17', 'V. Return F': '18',
            'V. Return G': '19', 'V. Return H': '20'
        }
        self.MixpointInputStateNames = {
            '00': '1', '01': '2', '02': '3', '03': '4', '04': '5', '05': '6',
            '06': '7', '07': '8', '08': '9', '09': '10', '10': '11', '11': '12',
            '13': 'V. Return A', '14': 'V. Return B', '15': 'V. Return C',
            '16': 'V. Return D', '17': 'V. Return E', '18': 'V. Return F',
            '19': 'V. Return G', '20': 'V. Return H'
        }

    def extr_25_5_128AT(self):
        self.MaxInputs = 12
        self.MaxOutputs = 8
        self.ExpansionBusInputStateValues = {
            '1': '21', '2': '22', '3': '23', '4': '24', '5': '25', '6': '26', '7': '27',
            '8': '28', '9': '29', '10': '30', '11': '31', '12': '32', '13': '33',
            '14': '34', '15': '35', '16': '36', '17': '37', '18': '38', '19': '39',
            '20': '40', '21': '41', '22': '42', '23': '43', '24': '44', '25': '45',
            '26': '46', '27': '47', '28': '48', '29': '49', '30': '50', '31': '51',
            '32': '52', '33': '53', '34': '54', '35': '55', '36': '56', '37': '57',
            '38': '58', '39': '59', '40': '60', '41': '61', '42': '62', '43': '63',
            '44': '64', '45': '65', '46': '66', '47': '67', '48': '68', '49': '69',
            '50': '70', '51': '71', '52': '72', '53': '73', '54': '74', '55': '75',
            '56': '76'
        }
        self.ExpansionBusInputStateNames = {
            '21': '1', '22': '2', '23': '3', '24': '4', '25': '5', '26': '6', '27': '7',
            '28': '8', '29': '9', '30': '10', '31': '11', '32': '12', '33': '13',
            '34': '14', '35': '15', '36': '16', '37': '17', '38': '18', '39': '19',
            '40': '20', '41': '21', '42': '22', '43': '23', '44': '24', '45': '25',
            '46': '26', '47': '27', '48': '28', '49': '29', '50': '30', '51': '31',
            '52': '32', '53': '33', '54': '34', '55': '35', '56': '36', '57': '37',
            '58': '38', '59': '39', '60': '40', '61': '41', '62': '42', '63': '43',
            '64': '44', '65': '45', '66': '46', '67': '47', '68': '48', '69': '49',
            '70': '50', '71': '51', '72': '52', '73': '53', '74': '54', '75': '55',
            '76': '56'
        }
        self.MixpointInputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03', '5': '04', '6': '05',
            '7': '06', '8': '07', '9': '08', '10': '09', '11': '10', '12': '11',
            'V. Return A': '13', 'V. Return B': '14', 'V. Return C': '15',
            'V. Return D': '16', 'V. Return E': '17', 'V. Return F': '18',
            'V. Return G': '19', 'V. Return H': '20'
        }
        self.MixpointInputStateNames = {
            '00': '1', '01': '2', '02': '3', '03': '4', '04': '5', '05': '6',
            '06': '7', '07': '8', '08': '9', '09': '10', '10': '11', '11': '12',
            '13': 'V. Return A', '14': 'V. Return B', '15': 'V. Return C',
            '16': 'V. Return D', '17': 'V. Return E', '18': 'V. Return F',
            '19': 'V. Return G', '20': 'V. Return H'
        }

    def extr_25_5_128P(self):
        self.MaxInputs = 13
        self.MaxOutputs = 9
        self.ExpansionBusInputStateValues = {
            '1': '21', '2': '22', '3': '23', '4': '24', '5': '25', '6': '26',
            '7': '27', '8': '28', '9': '29', '10': '30', '11': '31', '12': '32',
            '13': '33', '14': '34', '15': '35', '16': '36'
        }
        self.ExpansionBusInputStateNames = {
            '21': '1', '22': '2', '23': '3', '24': '4', '25': '5', '26': '6',
            '27': '7', '28': '8', '29': '9', '30': '10', '31': '11', '32': '12',
            '33': '13', '34': '14', '35': '15', '36': '16'
        }
        self.MixpointInputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03', '5': '04', '6': '05',
            '7': '06', '8': '07', '9': '08', '10': '09', '11': '10', '12': '11',
            'Telephone Rx': '12',
            'V. Return A': '13', 'V. Return B': '14', 'V. Return C': '15',
            'V. Return D': '16', 'V. Return E': '17', 'V. Return F': '18',
            'V. Return G': '19', 'V. Return H': '20'
        }
        self.MixpointInputStateNames = {
            '00': '1', '01': '2', '02': '3', '03': '4', '04': '5', '05': '6',
            '06': '7', '07': '8', '08': '9', '09': '10', '10': '11', '11': '12',
            '12': 'Telephone Rx',
            '13': 'V. Return A', '14': 'V. Return B', '15': 'V. Return C',
            '16': 'V. Return D', '17': 'V. Return E', '18': 'V. Return F',
            '19': 'V. Return G', '20': 'V. Return H'
        }

    def extr_25_5_128PAT(self):
        self.MaxInputs = 13
        self.MaxOutputs = 9
        self.ExpansionBusInputStateValues = {
            '1': '21',
            '2': '22',
            '3': '23',
            '4': '24',
            '5': '25',
            '6': '26',
            '7': '27',
            '8': '28',
            '9': '29',
            '10': '30',
            '11': '31',
            '12': '32',
            '13': '33',
            '14': '34',
            '15': '35',
            '16': '36',
            '17': '37',
            '18': '38',
            '19': '39',
            '20': '40',
            '21': '41',
            '22': '42',
            '23': '43',
            '24': '44',
            '25': '45',
            '26': '46',
            '27': '47',
            '28': '48',
            '29': '49',
            '30': '50',
            '31': '51',
            '32': '52',
            '33': '53',
            '34': '54',
            '35': '55',
            '36': '56',
            '37': '57',
            '38': '58',
            '39': '59',
            '40': '60',
            '41': '61',
            '42': '62',
            '43': '63',
            '44': '64',
            '45': '65',
            '46': '66',
            '47': '67',
            '48': '68',
            '49': '69',
            '50': '70',
            '51': '71',
            '52': '72',
            '53': '73',
            '54': '74',
            '55': '75',
            '56': '76'
        }
        self.ExpansionBusInputStateNames = {
            '21': '1',
            '22': '2',
            '23': '3',
            '24': '4',
            '25': '5',
            '26': '6',
            '27': '7',
            '28': '8',
            '29': '9',
            '30': '10',
            '31': '11',
            '32': '12',
            '33': '13',
            '34': '14',
            '35': '15',
            '36': '16',
            '37': '17',
            '38': '18',
            '39': '19',
            '40': '20',
            '41': '21',
            '42': '22',
            '43': '23',
            '44': '24',
            '45': '25',
            '46': '26',
            '47': '27',
            '48': '28',
            '49': '29',
            '50': '30',
            '51': '31',
            '52': '32',
            '53': '33',
            '54': '34',
            '55': '35',
            '56': '36',
            '57': '37',
            '58': '38',
            '59': '39',
            '60': '40',
            '61': '41',
            '62': '42',
            '63': '43',
            '64': '44',
            '65': '45',
            '66': '46',
            '67': '47',
            '68': '48',
            '69': '49',
            '70': '50',
            '71': '51',
            '72': '52',
            '73': '53',
            '74': '54',
            '75': '55',
            '76': '56'
        }
        self.MixpointInputStateValues = {
            '1': '00',
            '2': '01',
            '3': '02',
            '4': '03',
            '5': '04',
            '6': '05',
            '7': '06',
            '8': '07',
            '9': '08',
            '10': '09',
            '11': '10',
            '12': '11',
            'Telephone Rx': '12',
            'V. Return A': '13',
            'V. Return B': '14',
            'V. Return C': '15',
            'V. Return D': '16',
            'V. Return E': '17',
            'V. Return F': '18',
            'V. Return G': '19',
            'V. Return H': '20'
        }
        self.MixpointInputStateNames = {
            '00': '1',
            '01': '2',
            '02': '3',
            '03': '4',
            '04': '5',
            '05': '6',
            '06': '7',
            '07': '8',
            '08': '9',
            '09': '10',
            '10': '11',
            '11': '12',
            '12': 'Telephone Rx',
            '13': 'V. Return A',
            '14': 'V. Return B',
            '15': 'V. Return C',
            '16': 'V. Return D',
            '17': 'V. Return E',
            '18': 'V. Return F',
            '19': 'V. Return G',
            '20': 'V. Return H'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
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
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
