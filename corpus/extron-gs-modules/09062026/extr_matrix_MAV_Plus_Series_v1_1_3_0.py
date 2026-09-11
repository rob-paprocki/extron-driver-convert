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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {
            'MAV Plus 128 A': self.extr_15_63_128,
            'MAV Plus 1616 HDA': self.extr_15_63_1616,
            'MAV Plus 2412 A': self.extr_15_63_2412,
            'MAV Plus 3232 V': self.extr_15_63_3232,
            'MAV Plus 6432 A': self.extr_15_63_6432,
            'MAV Plus 6448 A': self.extr_15_63_6448,
            'MAV Plus 6464 A': self.extr_15_63_6464,
            'MAV Plus 128 AV': self.extr_15_63_128,
            'MAV Plus 128 AV RCA': self.extr_15_63_128,
            'MAV Plus 128 HD': self.extr_15_63_128,
            'MAV Plus 128 HDA': self.extr_15_63_128,
            'MAV Plus 128 SV': self.extr_15_63_128,
            'MAV Plus 128 SVA': self.extr_15_63_128,
            'MAV Plus 128 V': self.extr_15_63_128,
            'MAV Plus 1616 A': self.extr_15_63_1616,
            'MAV Plus 1616 AV': self.extr_15_63_1616,
            'MAV Plus 1616 SV': self.extr_15_63_1616,
            'MAV Plus 1616 SVA': self.extr_15_63_1616,
            'MAV Plus 1616 V': self.extr_15_63_1616,
            'MAV Plus 168 A': self.extr_15_63_168,
            'MAV Plus 168 AV': self.extr_15_63_168,
            'MAV Plus 168 HD': self.extr_15_63_168,
            'MAV Plus 168 HDA': self.extr_15_63_168,
            'MAV Plus 168 SV': self.extr_15_63_168,
            'MAV Plus 168 SVA': self.extr_15_63_168,
            'MAV Plus 168 V': self.extr_15_63_168,
            'MAV Plus 2412 AV': self.extr_15_63_2412,
            'MAV Plus 2412 V': self.extr_15_63_2412,
            'MAV Plus 2424 A': self.extr_15_63_2424,
            'MAV Plus 2424 AV': self.extr_15_63_2424,
            'MAV Plus 2424 V': self.extr_15_63_2424,
            'MAV Plus 3216 A': self.extr_15_63_3216,
            'MAV Plus 3216 AV': self.extr_15_63_3216,
            'MAV Plus 3216 V': self.extr_15_63_3216,
            'MAV Plus 3232 A': self.extr_15_63_3232,
            'MAV Plus 3232 AV': self.extr_15_63_3232,
            'MAV Plus 3248 A': self.extr_15_63_3248,
            'MAV Plus 3264 A': self.extr_15_63_3264,
            'MAV Plus 4832 A': self.extr_15_63_4832,
            'MAV Plus 4848 A': self.extr_15_63_4848,
            'MAV Plus 4864 A': self.extr_15_63_4864,
            'MAV Plus 2412 SV': self.extr_15_63_2412,
            'MAV Plus 2412 SVA': self.extr_15_63_2412,
            'MAV Plus 2424 SV': self.extr_15_63_2424,
            'MAV Plus 2424 SVA': self.extr_15_63_2424,
            'MAV Plus 3216 SV': self.extr_15_63_3216,
            'MAV Plus 3216 SVA': self.extr_15_63_3216,
            'MAV Plus 3232 SV': self.extr_15_63_3232,
            'MAV Plus 3232 SVA': self.extr_15_63_3232,
            'MAV Plus 88 HD': self.extr_15_63_88,
            'MAV Plus 88 HDA': self.extr_15_63_88,
            'MAV Plus 88 A': self.extr_15_63_88,
            'MAV Plus 88 AV': self.extr_15_63_88,
            'MAV Plus 88 SV': self.extr_15_63_88,
            'MAV Plus 88 SVA': self.extr_15_63_88,
            'MAV Plus 88 V': self.extr_15_63_88,
            'MAV Plus 1212 AV': self.extr_15_63_1212,
            'MAV Plus 816 HD': self.extr_15_63_816,
            'MAV Plus 816 HDA': self.extr_15_63_816,
            'MAV Plus 816 A': self.extr_15_63_816,
            'MAV Plus 816 V': self.extr_15_63_816,
            'MAV Plus 816 SV': self.extr_15_63_816,
            'MAV Plus 816 SVA': self.extr_15_63_816,
            'MAV Plus 816 AV': self.extr_15_63_816,
            'MAV Plus 3248 AM': self.extr_15_63_3248,
            'MAV Plus 3248 AV': self.extr_15_63_3248,
            'MAV Plus 3248 V': self.extr_15_63_3248,
            'MAV Plus 3264 AM': self.extr_15_63_3264,
            'MAV Plus 3264 AV': self.extr_15_63_3264,
            'MAV Plus 3264 V': self.extr_15_63_3264,
            'MAV Plus 4832 AM': self.extr_15_63_4832,
            'MAV Plus 4832 AV': self.extr_15_63_4832,
            'MAV Plus 4832 V': self.extr_15_63_4832,
            'MAV Plus 4848 AV': self.extr_15_63_4848,
            'MAV Plus 4848 AM': self.extr_15_63_4848,
            'MAV Plus 4848 V': self.extr_15_63_4848,
            'MAV Plus 4864 AM': self.extr_15_63_4864,
            'MAV Plus 4864 V': self.extr_15_63_4864,
            'MAV Plus 4864 AV': self.extr_15_63_4864,
            'MAV Plus 6432 AM': self.extr_15_63_6432,
            'MAV Plus 6432 AV': self.extr_15_63_6432,
            'MAV Plus 6432 V': self.extr_15_63_6432,
            'MAV Plus 6448 AM': self.extr_15_63_6448,
            'MAV Plus 6448 AV': self.extr_15_63_6448,
            'MAV Plus 6448 V': self.extr_15_63_6448,
            'MAV Plus 6464 V': self.extr_15_63_6464,
            'MAV Plus 6464 AM': self.extr_15_63_6464,
            'MAV Plus 6464 AV': self.extr_15_63_6464,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.refresh_matrix = False
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
 
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(rb'(?:Out(\d+) In(\d+) (All|Vid|Aud|RGB))|(?:In(\d+) (All|Vid|Aud|RGB))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(rb'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(rb'Amt(\d+)\*([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(rb'Rpr(\d+)\r\n'), self.__MatchQik, None)  # Response to a Set Preset Recall command
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(rb'Vgp00 Out(\d{2}) ([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(rb'Vgp00 Out(\d{2}) ([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'Vmt[01]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Amt[01]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Mut([0-3]+)\r\n'), self.__MatchMute, None)
            self.AddMatchString(compile(rb'Out(\d{2}) Vol(\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(rb'E(\d+)\r\n'), self.__MatchErrors, None)

            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')   

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword(None, None)

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
        self.UpdateAllMatrixTie(None, None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.Send('wvm\r')

    def __MatchMute(self, match, tag):
        Stat = match.group(1).decode()
        output = 1
        for i in Stat:
            if i == '0':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '1':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            elif i == '2':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '3':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            output += 1

    def __MatchQik(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        if self.OutputSize <= 16:
            command = 'w0*1*1vc\rw0*1*2vc\r'
        elif self.OutputSize <= 32:
            command = 'w0*1*1vc\rw0*1*2vc\rw0*17*1vc\rw0*17*2vc\r'
        elif self.OutputSize <= 48:
            command = 'w0*1*1vc\rw0*1*2vc\rw0*17*1vc\rw0*17*2vc\rw0*33*1vc\rw0*33*2vc'
        else:
            command = 'w0*1*1vc\rw0*1*2vc\rw0*17*1vc\rw0*17*2vc\rw0*33*1vc\rw0*33*2vc\rw0*49*1vc\rw0*49*2vc\r'            
        self.__SetHelper('RefreshMatrix', command, value, qualifier)

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)
        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)
        for input_ in range(self.InputSize):
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Video'})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        av_counter_max = 16 if self.refresh_matrix else self.OutputSize
        opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

        for i in input_list:
            if tag == 'Audio':
                self.audio_status_counter += 1
            elif tag == 'Video':
                self.video_status_counter += 1

            if i != '--':
                if i != '00':
                    if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag

                current_output += 1

        if self.audio_status_counter == av_counter_max and self.video_status_counter == av_counter_max:
            self.refresh_matrix = False
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        Value = {
            'Off': '0',
            'On': '1',
        }[value]

        Channel = qualifier['Output']

        if 1 <= int(Channel) <= self.OutputSize:
            self.__SetHelper('AudioMute', '{0}*{1}z'.format(Channel, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        Channel = qualifier['Output']
        if 1 <= int(Channel) <= self.OutputSize:
            self.__UpdateHelper('AudioMute', '{0}z'.format(Channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, qualifier):

        Value = {
            '0': 'Off',
            '1': 'On'
        }[match.group(2).decode()]

        Channel = str(int(match.group(1)))
        self.WriteStatus('AudioMute', Value, {'Output': Channel})

    def SetExecutiveMode(self, value, qualifier):

        Value = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }[value]

        self.__SetHelper('ExecutiveMode', '{0}X'.format(Value), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        Value = {
            '1': 'Mode 1',
                 '2': 'Mode 2',
                 '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('ExecutiveMode', Value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        Value = {
            'Off': '0',
            'On': '1',
        }[value]

        self.__SetHelper('GlobalAudioMute', '{0}*z'.format(Value), value, qualifier)
        self.UpdateMute(None, None)

    def SetGlobalVideoMute(self, value, qualifier):

        Value = {
            'Off': '0',
            'On': '1',
        }[value]

        self.__SetHelper('GlobalVideoMute', '{0}*b'.format(Value), value, qualifier)
        self.UpdateMute(None, None)

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio': '\x24',
            'Video': '\x26',
            'Audio/Video': '\x21'
        }

        input_ = int(qualifier['Input'])
        output = qualifier['Output']
        tieType = qualifier['Tie Type']
        outrange = ['All']
        for i in range(1, self.OutputSize + 1):
            outrange.append(str(i))

        if output not in outrange:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif input_ < 0 or input_ > self.InputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            output = '' if output == 'All' else output
            self.__SetHelper('MatrixTieCommand', '{0}*{1}{2}'.format(input_, output, TieTypeValues[tieType]), input_, qualifier)

    def __MatchOutputTieStatus(self, match, qualifier):
        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video',
        }
        output = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output - 1]
                if i != input_ - 1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output - 1] = 'Untied'
                elif i == input_ - 1:
                    self.matrix_tie_status[i][output - 1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output - 1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_ - 1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output - 1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output - 1] = tietype
                elif input_ == 0 or i != input_ - 1:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output - 1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output - 1] = opTag

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video',
        }
        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]

        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input - 1:
                        if self.matrix_tie_status[input_][output] == op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[input_][output] = tietype
                    else:
                        if self.matrix_tie_status[input_][output] == 'Audio/Video':
                            self.matrix_tie_status[input_][output] = op_tie_type
                        elif self.matrix_tie_status[input_][output] != op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Untied'

        elif tietype == 'Audio/Video':
            for output in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input - 1:
                        self.matrix_tie_status[input_][output] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= self.MaxPresetSize:
            self.__SetHelper('PresetRecall', '{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= self.MaxPresetSize:
            self.__SetHelper('PresetSave', '{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        valueStates = {
            '1 - 16': 'w0*1*1vc\rw0*1*2vc\r',
            '17 - 32': 'w0*17*1vc\rw0*17*2vc\r',
            '33 - 48': 'w0*33*1vc\rw0*33*2vc\r',
            '49 - 64': 'w0*49*1vc\rw0*49*2vc\r',
        }

        if value == 'All' or value in valueStates:
            if value == 'All':
                if self.OutputSize <= 16:
                    command = 'w0*1*1vc\rw0*1*2vc\r'
                elif self.OutputSize <= 32:
                    command = 'w0*1*1vc\rw0*1*2vc\rw0*17*1vc\rw0*17*2vc\r'
                elif self.OutputSize <= 48:
                    command = 'w0*1*1vc\rw0*1*2vc\rw0*17*1vc\rw0*17*2vc\rw0*33*1vc\rw0*33*2vc'
                else:
                    command = 'w0*1*1vc\rw0*1*2vc\rw0*17*1vc\rw0*17*2vc\rw0*33*1vc\rw0*33*2vc\rw0*49*1vc\rw0*49*2vc\r'
            else:
                command = valueStates[value]
                self.refresh_matrix = True

            self.audio_status_counter = 0
            self.video_status_counter = 0
            self.__SetHelper('RefreshMatrix', command, value, qualifier)  # delay of 5 seconds
        else:
            self.Discard('Invalid Command for SetRefreshMatrix')

    def SetVideoMute(self, value, qualifier):

        Value = {
            'Off': '0',
            'On': '1'
        }[value]

        Channel = qualifier['Output']

        if 1 <= int(Channel) <= self.OutputSize:
            self.__SetHelper('VideoMute', '{0}*{1}b'.format(Channel, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):
        Channel = qualifier['Output']

        if 1 <= int(Channel) <= self.OutputSize:
            self.__UpdateHelper('VideoMute', '{0}b'.format(Channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):

        Value = {
            '0': 'Off',
            '1': 'On'
        }[match.group(2).decode()]

        Output = str(int(match.group(1)))

        self.WriteStatus('VideoMute', Value, {'Output': Output})

    def SetVolume(self, value, qualifier):

        Channel = qualifier['Output']

        if 1 <= int(Channel) <= self.OutputSize and 0 <= value <= 64:
            self.__SetHelper('Volume', '{0}*{1}v'.format(Channel, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        Channel = qualifier['Output']
        if 1 <= int(Channel) <= self.OutputSize:
            self.__UpdateHelper('Volume', '{0}V'.format(Channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, qualifier):
        self.WriteStatus('Volume', int(match.group(2)), {'Output': str(int(match.group(1)))})

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

    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {

            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '17': 'Timeout (caused only by direct write of global presets)',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename / file not found',

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

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

        self.VerboseDisabled = True
        self.refresh_matrix = False

    def extr_15_63_88(self):

        self.InputSize = 8
        self.OutputSize = 8
        self.MaxPresetSize = 32

    def extr_15_63_1616(self):

        self.InputSize = 16
        self.OutputSize = 16
        self.MaxPresetSize = 32

    def extr_15_63_168(self):

        self.InputSize = 16
        self.OutputSize = 8
        self.MaxPresetSize = 32

    def extr_15_63_816(self):

        self.InputSize = 8
        self.OutputSize = 16
        self.MaxPresetSize = 32

    def extr_15_63_128(self):

        self.InputSize = 12
        self.OutputSize = 8
        self.MaxPresetSize = 32

    def extr_15_63_1212(self):

        self.InputSize = 12
        self.OutputSize = 12
        self.MaxPresetSize = 32

    def extr_15_63_2412(self):

        self.InputSize = 24
        self.OutputSize = 12
        self.MaxPresetSize = 132

    def extr_15_63_2424(self):

        self.InputSize = 24
        self.OutputSize = 24
        self.MaxPresetSize = 132

    def extr_15_63_3216(self):

        self.InputSize = 32
        self.OutputSize = 16
        self.MaxPresetSize = 132

    def extr_15_63_3232(self):

        self.InputSize = 32
        self.OutputSize = 32
        self.MaxPresetSize = 132

    def extr_15_63_3248(self):

        self.InputSize = 32
        self.OutputSize = 48
        self.MaxPresetSize = 64

    def extr_15_63_3264(self):

        self.InputSize = 32
        self.OutputSize = 64
        self.MaxPresetSize = 64

    def extr_15_63_4832(self):

        self.InputSize = 48
        self.OutputSize = 32
        self.MaxPresetSize = 64

    def extr_15_63_4848(self):

        self.InputSize = 48
        self.OutputSize = 48
        self.MaxPresetSize = 64

    def extr_15_63_4864(self):

        self.InputSize = 48
        self.OutputSize = 64
        self.MaxPresetSize = 64

    def extr_15_63_6432(self):

        self.InputSize = 64
        self.OutputSize = 32
        self.MaxPresetSize = 64

    def extr_15_63_6448(self):

        self.InputSize = 64
        self.OutputSize = 48
        self.MaxPresetSize = 64

    def extr_15_63_6464(self):

        self.InputSize = 64
        self.OutputSize = 64
        self.MaxPresetSize = 64

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
