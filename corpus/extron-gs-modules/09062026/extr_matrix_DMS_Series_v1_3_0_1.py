from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'DMS 3600': self.extr_15_96_DMS_3600,
            'DMS 1600': self.extr_15_96_DMS_1600,
            'DMS 3200': self.extr_15_96_DMS_3200,
            'DMS 2000': self.extr_15_96_DMS_2000,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'EDIDAssignment': {'Parameters': ['Input'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        self.refresh_matrix = False
        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'EdidA(\d+)\*(\d+)\r\n'), self.__MatchEDIDAssignment, None)
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|RGB))|(?:In(\d+) (All|Vid|RGB))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'Out(\d+) In(\d+) (RGB|All|Vid)\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frq0+\*([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Rpr(\d+)\r\n'), self.__MatchRecallPreset, None)
            self.AddMatchString(compile(b'Vgp00 Out(\d+)\*([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vmt[0-1]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Mut([0-1]+)\r\n'), self.__MatchMute, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchError, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
        else:
            if self.devicePassword:
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
        self.UpdateAllMatrixTie(None, None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.__UpdateHelper('Mute', 'wVM\r', None, None)

    def __MatchMute(self, match, tag):
        muteStates = {
            '0': 'Off',
            '1': 'On'
        }

        stat = match.group(1).decode()
        output = 1
        for i in stat:
            self.WriteStatus('VideoMute', muteStates[i], {'Output': str(output)})
            output += 1

    def __MatchQik(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def SetMatrixRefresh(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def __MatchRecallPreset(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.Debug = True
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]

        self.__UpdateHelper('RefreshMatrix', 'w0*1*1VC\r', None, None)
        if self.OutputSize > 16:
            self.__UpdateHelper('RefreshMatrix', 'w0*17*1VC\r', None, None)
        if self.OutputSize > 32:
            self.__UpdateHelper('RefreshMatrix', 'w0*33*1VC\r', None, None)

    def writeInputTieStatus(self, tie, output=None):

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def writeOutputTieStatus(self, tie, output=None):

        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:

                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1)})
                    VideoList.add(output)

        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1)})

    def __MatchAllMatrixTie(self, match, tag):

        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        counter_max = 16 if self.refresh_matrix else self.OutputSize

        for i in input_list:

            self.video_status_counter += 1
            if i != '--':
                if i != '00':
                    self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag
                current_output += 1

        if self.video_status_counter == counter_max:
            self.refresh_matrix = False
            self.writeInputTieStatus('All')
            self.writeOutputTieStatus('All')

    def UpdateEDIDAssignment(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            EDIDAssignmentCmdString = 'wA{0}EDID\r'.format(input_)
            self.__UpdateHelper('EDIDAssignment', EDIDAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEDIDAssignment')

    def __MatchEDIDAssignment(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = self.EDIDValues[str(int(match.group(2).decode()))]
        self.WriteStatus('EDIDAssignment', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On': '1',
            'Off': '0'
        }

        self.__SetHelper('ExecutiveMode', '{0}X'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            b'1': 'On',
            b'0': 'Off',
        }

        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1)], None)

    def SetGlobalVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }

        self.__SetHelper('GlobalVideoMute', '{0}*B'.format(VideoMuteState[value]), value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):
        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatus = {
            '1': 'Active',
            '0': 'Not Active',
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for input_ in signal:
            self.WriteStatus('InputSignalStatus', InputSignalStatus[input_], {'Input': str(inputNumber)})
            inputNumber += 1

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = int(qualifier['Input'])
        output = qualifier['Output']

        if output == 'All':
            cmdStr = ''
            for o in range(1, self.OutputSize + 1):
                cmdStr = '{0}{1}*{2}&'.format(cmdStr, input_, o)
            self.__SetHelper('MatrixTieCommand', cmdStr, value, qualifier)
        else:
            self.__SetHelper('MatrixTieCommand', '{0}*{1}&'.format(input_, output), value, qualifier)

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def __MatchOutputTieStatus(self, match, qualifier):

        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):

        output = int(match.group(1))
        input_ = int(match.group(2))

        for i in range(self.InputSize):
            current_tie = self.matrix_tie_status[i][output - 1]
            if i == input_ - 1:
                self.matrix_tie_status[i][output - 1] = 'Video'
            elif input_ == 0 or i != input_ - 1:
                if current_tie == 'Video':
                    self.matrix_tie_status[i][output - 1] = 'Untied'

        self.writeOutputTieStatus('Individual', output)
        self.writeInputTieStatus('Individual', output)

    def __MatchAllTie(self, match, qualifier):

        new_input = int(match.group(4))
        for output in range(self.OutputSize):
            for input_ in range(self.InputSize):
                if input_ == new_input - 1:
                    self.matrix_tie_status[input_][output] = 'Video'

        self.writeInputTieStatus('All')
        self.writeOutputTieStatus('All')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetRecall', '{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetSave', '{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        state = {
            '1 - 16': 'w0*1*1VC\r',
            '17 - 20': 'w0*17*1VC\r',
            '17 - 32': 'w0*17*1VC\r',
            '33 - 36': 'w0*33*1VC\r'
        }

        if not value or value == 'All':
            self.UpdateAllMatrixTie(value, qualifier)
        else:
            self.refresh_matrix = True
            self.video_status_counter = 0
            self.__SetHelper('RefreshMatrix', state[value], value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__SetHelper('VideoMute', '{0}*{1}B'.format(channel, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__UpdateHelper('VideoMute', '{0}B'.format(channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }

        self.WriteStatus('VideoMute', VideoMuteName[match.group(2)], {'Output': str(int(match.group(1)))})

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

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number (too large)',
            '13': 'Invalid value (out of range)',
            '14': 'Illegal command for this configuration',
            '17': 'Timeout (caused only by direct write of global presets)',
            '21': 'Invalid room number',
            '24': 'Privilege violation (Ethernet)'
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

    def extr_15_96_DMS_1600(self):

        self.InputSize = 16
        self.OutputSize = 16
        self.EDIDValues = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5',
            '6': 'Output 6',
            '7': 'Output 7',
            '8': 'Output 8',
            '9': 'Output 9',
            '10': 'Output 10',
            '11': 'Output 11',
            '12': 'Output 12',
            '13': 'Output 13',
            '14': 'Output 14',
            '15': 'Output 15',
            '16': 'Output 16',
            '17': '640x480 @ 60Hz',
            '18': '640x480 @ 75Hz',
            '19': '800x600 @ 60Hz',
            '20': '800x600 @ 75Hz',
            '21': '852x480 @ 60Hz',
            '22': '852x480 @ 75Hz',
            '23': '1024x768 @ 60Hz',
            '24': '1024x768 @ 75Hz',
            '25': '1024x852 @ 60Hz',
            '26': '1024x852 @ 75Hz',
            '27': '1280x768 @ 60Hz',
            '28': '1280x768 @ 75Hz',
            '29': '1280x1024 @ 60Hz',
            '30': '1280x1024 @ 75Hz',
            '31': '1365x768 @ 60Hz',
            '32': '1365x768 @ 75Hz',
            '33': '1366x768 @ 60Hz',
            '34': '1366x768 @ 75Hz',
            '35': '1400x1050 @ 60Hz',
            '36': '1600x1200 @ 60Hz',
            '37': '1920x1200 @ 60Hz',
            '38': '480p @ 60Hz',
            '39': '576p @ 50Hz',
            '40': '720p @ 50Hz',
            '41': '720p @ 60Hz',
            '42': '1080p @ 60Hz',
            '43': '1080i @ 60Hz',
            '44': '1080p @ 50Hz',
            '45': '1080p @ 60Hz, stereo',
            '46': 'User Assigned 1',
            '47': 'User Assigned 2',
            '48': 'User Assigned 3',
            '49': 'User Assigned 4',
            '50': 'User Assigned 5',
            '51': 'User Assigned 6',
            '52': 'User Assigned 7',
            '53': 'User Assigned 8'
        }

    def extr_15_96_DMS_2000(self):

        self.InputSize = 20
        self.OutputSize = 20
        self.EDIDValues = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5',
            '6': 'Output 6',
            '7': 'Output 7',
            '8': 'Output 8',
            '9': 'Output 9',
            '10': 'Output 10',
            '11': 'Output 11',
            '12': 'Output 12',
            '13': 'Output 13',
            '14': 'Output 14',
            '15': 'Output 15',
            '16': 'Output 16',
            '17': 'Output 17',
            '18': 'Output 18',
            '19': 'Output 19',
            '20': 'Output 20',
            '21': '640x480 @ 60Hz',
            '22': '640x480 @ 75Hz',
            '23': '800x600 @ 60Hz',
            '24': '800x600 @ 75Hz',
            '25': '852x480 @ 60Hz',
            '26': '852x480 @ 75Hz',
            '27': '1024x768 @ 60Hz',
            '28': '1024x768 @ 75Hz',
            '29': '1024x852 @ 60Hz',
            '30': '1024x852 @ 75Hz',
            '31': '1280x768 @ 60Hz',
            '32': '1280x768 @ 75Hz',
            '33': '1280x1024 @ 60Hz',
            '34': '1280x1024 @ 75Hz',
            '35': '1365x768 @ 60Hz',
            '36': '1365x768 @ 75Hz',
            '37': '1366x768 @ 60Hz',
            '38': '1366x768 @ 75Hz',
            '39': '1400x1050 @ 60Hz',
            '40': '1600x1200 @ 60Hz',
            '41': '1920x1200 @ 60Hz',
            '42': '480p @ 60Hz',
            '43': '576p @ 50Hz',
            '44': '720p @ 50Hz',
            '45': '720p @ 60Hz',
            '46': '1080p @ 60Hz',
            '47': '1080i @ 60Hz',
            '48': '1080p @ 50Hz',
            '49': '1080p @ 60Hz, stereo',
            '50': 'User Assigned 1',
            '51': 'User Assigned 2',
            '52': 'User Assigned 3',
            '53': 'User Assigned 4',
            '54': 'User Assigned 5',
            '55': 'User Assigned 6',
            '56': 'User Assigned 7',
            '57': 'User Assigned 8'
        }

    def extr_15_96_DMS_3200(self):

        self.InputSize = 32
        self.OutputSize = 32
        self.EDIDValues = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5',
            '6': 'Output 6',
            '7': 'Output 7',
            '8': 'Output 8',
            '9': 'Output 9',
            '10': 'Output 10',
            '11': 'Output 11',
            '12': 'Output 12',
            '13': 'Output 13',
            '14': 'Output 14',
            '15': 'Output 15',
            '16': 'Output 16',
            '17': 'Output 17',
            '18': 'Output 18',
            '19': 'Output 19',
            '20': 'Output 20',
            '21': 'Output 21',
            '22': 'Output 22',
            '23': 'Output 23',
            '24': 'Output 24',
            '25': 'Output 25',
            '26': 'Output 26',
            '27': 'Output 27',
            '28': 'Output 28',
            '29': 'Output 29',
            '30': 'Output 30',
            '31': 'Output 31',
            '32': 'Output 32',
            '33': '640x480 @ 60Hz',
            '34': '640x480 @ 75Hz',
            '35': '800x600 @ 60Hz',
            '36': '800x600 @ 75Hz',
            '37': '852x480 @ 60Hz',
            '38': '852x480 @ 75Hz',
            '39': '1024x768 @ 60Hz',
            '40': '1024x768 @ 75Hz',
            '41': '1024x852 @ 60Hz',
            '42': '1024x852 @ 75Hz',
            '43': '1280x768 @ 60Hz',
            '44': '1280x768 @ 75Hz',
            '45': '1280x1024 @ 60Hz',
            '46': '1280x1024 @ 75Hz',
            '47': '1365x768 @ 60Hz',
            '48': '1365x768 @ 75Hz',
            '49': '1366x768 @ 60Hz',
            '50': '1366x768 @ 75Hz',
            '51': '1400x1050 @ 60Hz',
            '52': '1600x1200 @ 60Hz',
            '53': '1920x1200 @ 60Hz',
            '54': '480p @ 60Hz',
            '55': '576p @ 50Hz',
            '56': '720p @ 50Hz',
            '57': '720p @ 60Hz',
            '58': '1080p @ 60Hz',
            '59': '1080i @ 60Hz',
            '60': '1080p @ 50Hz',
            '61': '1080p @ 60Hz, stereo',
            '62': 'User Assigned 1',
            '63': 'User Assigned 2',
            '64': 'User Assigned 3',
            '65': 'User Assigned 4',
            '66': 'User Assigned 5',
            '67': 'User Assigned 6',
            '68': 'User Assigned 7',
            '69': 'User Assigned 8'
        }

    def extr_15_96_DMS_3600(self):

        self.InputSize = 36
        self.OutputSize = 36
        self.EDIDValues = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5',
            '6': 'Output 6',
            '7': 'Output 7',
            '8': 'Output 8',
            '9': 'Output 9',
            '10': 'Output 10',
            '11': 'Output 11',
            '12': 'Output 12',
            '13': 'Output 13',
            '14': 'Output 14',
            '15': 'Output 15',
            '16': 'Output 16',
            '17': 'Output 17',
            '18': 'Output 18',
            '19': 'Output 19',
            '20': 'Output 20',
            '21': 'Output 21',
            '22': 'Output 22',
            '23': 'Output 23',
            '24': 'Output 24',
            '25': 'Output 25',
            '26': 'Output 26',
            '27': 'Output 27',
            '28': 'Output 28',
            '29': 'Output 29',
            '30': 'Output 30',
            '31': 'Output 31',
            '32': 'Output 32',
            '33': 'Output 33',
            '34': 'Output 34',
            '35': 'Output 35',
            '36': 'Output 36',
            '37': '640x480 @ 60Hz',
            '38': '640x480 @ 75Hz',
            '39': '800x600 @ 60Hz',
            '40': '800x600 @ 75Hz',
            '41': '852x480 @ 60Hz',
            '42': '852x480 @ 75Hz',
            '43': '1024x768 @ 60Hz',
            '44': '1024x768 @ 75Hz',
            '45': '1024x852 @ 60Hz',
            '46': '1024x852 @ 75Hz',
            '47': '1280x768 @ 60Hz',
            '48': '1280x768 @ 75Hz',
            '49': '1280x1024 @ 60Hz',
            '50': '1280x1024 @ 75Hz',
            '51': '1365x768 @ 60Hz',
            '52': '1365x768 @ 75Hz',
            '53': '1366x768 @ 60Hz',
            '54': '1366x768 @ 75Hz',
            '55': '1400x1050 @ 60Hz',
            '56': '1600x1200 @ 60Hz',
            '57': '1920x1200 @ 60Hz',
            '58': '480p @ 60Hz',
            '59': '576p @ 50Hz',
            '60': '720p @ 50Hz',
            '61': '720p @ 60Hz',
            '62': '1080p @ 60Hz',
            '63': '1080i @ 60Hz',
            '64': '1080p @ 50Hz',
            '65': '1080p @ 60Hz, stereo',
            '66': 'User Assigned 1',
            '67': 'User Assigned 2',
            '68': 'User Assigned 3',
            '69': 'User Assigned 4',
            '70': 'User Assigned 5',
            '71': 'User Assigned 6',
            '72': 'User Assigned 7',
            '73': 'User Assigned 8'
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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        Command = self.Commands[command]
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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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
