from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output', 'Plane'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FanStatus': {'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output', 'Plane'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Plane', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Plane', 'Tie Type'], 'Status': {}},
            'PlaneAudioMute': {'Parameters': ['Plane'], 'Status': {}},
            'PlanePresetRecall': {'Parameters': ['Plane'], 'Status': {}},
            'PlanePresetSave': {'Parameters': ['Plane'], 'Status': {}},
            'PlaneVideoMute': {'Parameters': ['Plane'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'TemperatureStatus': {'Status': {}},
            'VideoMute': {'Parameters': ['Output', 'Plane'], 'Status': {}},
            'VoltageLevel': {'Status': {}},
            'Volume': {'Parameters': ['Output', 'Plane'], 'Status': {}},
        }

        self.InputSize = 16
        self.OutputSize = 16
        self.PlaneList = {}
        self.refresh_matrix = False

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(\d+)Amt(\d+)\*([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Sts05\*(.*)\r\n'), self.__MatchFanStatus, None)
            self.AddMatchString(re.compile(b'Vgp(\d{2})\*00 Out(\d{2}) ([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(re.compile(b'Vgp(\d{2})\*00 Out(\d{2}) ([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(re.compile(b'(\d+)Out(\d+) In(\d+) (\w{3})\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'Rpr\d+\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'Sts04\*(.*)\r\n'), self.__MatchTemperatureStatus, None)
            self.AddMatchString(re.compile(b'(\d+)Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Sts01\*(.*)\r\n'), self.__MatchVoltageLevel, None)
            self.AddMatchString(re.compile(b'(\d+)Out(\d{2}) Vol(\d{2})\r\n'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'Reconfig\r\n'), self.__MatchReconfig, None)
            self.AddMatchString(re.compile(b'Inf00\*([-VAX0-9 ]*)\r\n'), self.__MatchIResponse, None)

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(re.compile(b'Login User\r\n'), self.__MatchLoginUser, None)



    def SetPassword(self):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 2:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword()

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
        self.SetRefreshMatrix('All', None)

    def __MatchReconfig(self, match, tag):
        self.SetRefreshMatrix('All', None)

    def __MatchIResponse(self, match, tag):
        list = match.group(1).decode()
        plane = re.findall(re.compile('V[-0-9]{2}X[-0-9]{2}A[-0-9]{2}X[-0-9]{2}'), list)
        planeNumber = 0
        for i in plane:
            output = re.findall(re.compile('\d{2}'), i)
            if output:
                VidIn = int(output[0])
                VidOut = int(output[1])
                AudIn = int(output[2])
                AudOut = int(output[3])
                self.PlaneList[str(planeNumber)] = {'VidIn': VidIn, 'VidOut': VidOut, 'AudIn': AudIn, 'AudOut': AudOut}
            planeNumber += 1
        self.UpdateAllMatrixTie(None, None)

    def __MatchQik(self, match, tag):

        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = {}
        for plane in self.PlaneList:
            self.matrix_tie_status[plane] = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
            if self.PlaneList[plane]['AudOut']:
                self.__UpdateHelper('RefreshMatrix', '\x1BG{0}*0*1*2vc\r'.format(plane), value, None)
            if self.PlaneList[plane]['VidOut']:
                self.__UpdateHelper('RefreshMatrix', '\x1BG{0}*0*1*1vc\r'.format(plane), value, None)

    def __MatchAllMatrixTie(self, match, tag):

        plane = str(int(match.group(1)))
        current_output = int(match.group(2))
        input_list = match.group(3).decode().split()  # list of input that tied to output.
        aud_counter = 0
        vid_counter = 0
        for p in self.PlaneList:
            if self.PlaneList[p]['AudOut'] and self.PlaneList[p]['VidOut']:
                aud_counter += self.OutputSize
                vid_counter += self.OutputSize
            elif self.PlaneList[p]['AudOut']:
                aud_counter += self.OutputSize
            elif self.PlaneList[p]['VidOut']:
                vid_counter += self.OutputSize

        aud_counter_max = self.OutputSize if self.refresh_matrix and self.PlaneList[plane]['AudOut'] else aud_counter
        vid_counter_max = self.OutputSize if self.refresh_matrix and self.PlaneList[plane]['VidOut'] else vid_counter
        opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

        for i in input_list:

            if tag == 'Audio':
                self.audio_status_counter += 1
            elif tag == 'Video':
                self.video_status_counter += 1

            if i != '--':
                if i != '00':
                    if self.matrix_tie_status[plane][int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[plane][int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[plane][int(i) - 1][int(current_output - 1)] = tag

                current_output += 1

        if self.audio_status_counter == aud_counter_max and self.video_status_counter == vid_counter_max:
            self.refresh_matrix = False
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for plane in self.PlaneList:
            for input_ in range(self.InputSize):
                for output in output_range:
                    self.WriteStatus('InputTieStatus', self.matrix_tie_status[plane][input_][output], {'Plane': plane, 'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = {}
        VideoList = {}

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for plane in self.PlaneList:
            AudioList[plane] = set()
            VideoList[plane] = set()
            for input_ in range(self.InputSize):
                for output in output_range:

                    tietype = self.matrix_tie_status[plane][input_][output]
                    if tietype == 'Audio/Video':
                        for tie_type in ['Audio', 'Video', 'Audio/Video']:
                            self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Plane': plane, 'Output': str(output + 1), 'Tie Type': tie_type})
                        AudioList[plane].add(output)
                        VideoList[plane].add(output)
                    elif tietype == 'Audio':
                        self.WriteStatus('OutputTieStatus', '0', {'Plane': plane, 'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Plane': plane, 'Output': str(output + 1), 'Tie Type': 'Audio'})
                        AudioList[plane].add(output)
                    elif tietype == 'Video':
                        self.WriteStatus('OutputTieStatus', '0', {'Plane': plane, 'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Plane': plane, 'Output': str(output + 1), 'Tie Type': 'Video'})
                        VideoList[plane].add(output)

            for o in output_range:
                if o not in VideoList[plane]:
                    self.WriteStatus('OutputTieStatus', '0', {'Plane': plane, 'Output': str(o + 1), 'Tie Type': 'Video'})
                if o not in AudioList[plane]:
                    self.WriteStatus('OutputTieStatus', '0', {'Plane': plane, 'Output': str(o + 1), 'Tie Type': 'Audio'})
                if o not in VideoList[plane] and o not in AudioList[plane]:
                    self.WriteStatus('OutputTieStatus', '0', {'Plane': plane, 'Output': str(o + 1), 'Tie Type': 'Audio/Video'})

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        output = int(qualifier['Output'])
        plane = int(qualifier['Plane'])
        if 1 <= output <= self.OutputSize and plane in range(16):
            AudioMuteString = '{0}*{1}*{2}Z'.format(plane, output, AudioMuteState[value])
            self.__SetHelper('AudioMute', AudioMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        output = int(qualifier['Output'])
        plane = int(qualifier['Plane'])
        if 1 <= output <= self.OutputSize and plane in range(16):
            AudioMuteString = '{0}*{1}Z'.format(plane, output)
            self.__UpdateHelper('AudioMute', AudioMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        AudioMuteName = {
            0: 'Off',
            1: 'On',
        }

        value = AudioMuteName[int(match.group(3))]
        output = str(int(match.group(2)))
        plane = str(int(match.group(1)))
        if output != '0':
            self.WriteStatus('AudioMute', value, {'Output': output, 'Plane': plane})
        elif plane in self.PlaneList:
            outputRange = range(1, self.PlaneList[plane]['AudOut'] + 1)
            for output in outputRange:
                self.WriteStatus('AudioMute', value, {'Output': str(output), 'Plane': plane})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }
        ExecutiveModeString = '{0}x'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'x', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            b'1': 'Mode 1',
            b'2': 'Mode 2',
            b'0': 'Off',
        }

        value = ExecutiveModeName[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateFanStatus(self, value, qualifier):

        FanStatusCmdString = '5S'
        self.__UpdateHelper('FanStatus', FanStatusCmdString, value, qualifier)

    def __MatchFanStatus(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('FanStatus', value, None)

    def SetMatrixTieCommand(self, value, qualifier):

        input = int(qualifier['Input'])
        output = int(qualifier['Output'])
        plane = int(qualifier['Plane'])
        tieType = qualifier['Tie Type']

        if output <= 0 or output > self.OutputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif input < 0 or input > self.InputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif plane < 0 or plane > 15:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            TieTypeValues = {
                'Audio': '{0}*{1}*{2}$'.format(plane, input, output),
                'Video': '{0}*{1}*{2}%'.format(plane, input, output),
                'Audio/Video': '{0}*{1}*{2}!'.format(plane, input, output),
            }

            self.__SetHelper('MatrixTieCommand', TieTypeValues[tieType], input, qualifier)

    def UpdateOutputTieStatus(self, value, qualifier):

        output = int(qualifier['Output'])
        plane = qualifier['Plane']
        tieType = qualifier['Tie Type']
        if plane not in self.PlaneList:
            self.Discard('Invalid Command for UpdateOutputTieStatus')
        elif self.PlaneList[plane]['VidOut'] < output < 0:
            self.Discard('Invalid Command for UpdateOutputTieStatus')
        else:
            TieTypeValues = {
                'Audio': '{0}*{1}$'.format(plane, output),
                'Video': '{0}*{1}%'.format(plane, output),
                'Audio/Video': '{0}*{1}!'.format(plane, output)
            }
            self.__UpdateHelper('OutputTieStatus', TieTypeValues[tieType], value, qualifier)

    def __MatchOutputTieStatus(self, match, qualifier):

        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video',
        }

        plane = str(int(match.group(1)))
        output = int(match.group(2))
        input_ = int(match.group(3))
        tietype = TieTypeStates[match.group(4).decode()]

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[plane][i][output - 1]
                if i != input_ - 1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[plane][i][output - 1] = 'Untied'
                elif i == input_ - 1:
                    self.matrix_tie_status[plane][i][output - 1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[plane][i][output - 1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_ - 1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[plane][i][output - 1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[plane][i][output - 1] = tietype
                elif input_ == 0 or i != input_ - 1:
                    if current_tie == tietype:
                        self.matrix_tie_status[plane][i][output - 1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[plane][i][output - 1] = opTag

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def SetPlaneAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        plane = qualifier['Plane']
        if plane in self.PlaneList:
            AudioMuteString = '{0}*{1}*Z'.format(plane, AudioMuteState[value])
            self.__SetHelper('PlaneAudioMute', AudioMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaneAudioMute')

    def SetPlanePresetRecall(self, value, qualifier):

        plane = qualifier['Plane']
        if 1 <= int(value) <= 10 and int(plane) in range(16):
            PlanePresetString = '{0}*{1}*0.'.format(plane, value)
            self.__SetHelper('PlanePresetRecall', PlanePresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlanePresetRecall')

    def SetPlanePresetSave(self, value, qualifier):

        plane = qualifier['Plane']
        if 1 <= int(value) <= 10 and int(plane) in range(16):
            PlanePresetString = '{0}*{1}*0,'.format(plane, value)
            self.__SetHelper('PlanePresetSave', PlanePresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlanePresetSave')

    def SetPlaneVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        plane = qualifier['Plane']
        if plane in self.PlaneList:
            VideoMuteString = '{0}*{1}*B'.format(plane, VideoMuteState[value])
            self.__SetHelper('PlaneVideoMute', VideoMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaneVideoMute')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetRecallString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetSaveString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):
        self.Debug = True
        if value == 'All':
            self.__UpdateHelper('RefreshMatrix', 'i', None, None)
        elif int(value) in range(16) and value in self.PlaneList:
            if self.PlaneList[value]['AudOut']:
                self.__UpdateHelper('RefreshMatrix', '\x1BG{0}*0*1*2vc\r'.format(value), value, None)
            if self.PlaneList[value]['VidOut']:
                self.__UpdateHelper('RefreshMatrix', '\x1BG{0}*0*1*1vc\r'.format(value), value, None)
            self.refresh_matrix = True
        else:
            self.Discard('Invalid Command for SetRefreshMatrix')

    def UpdateTemperatureStatus(self, value, qualifier):

        TemperatureStatusCmdString = '4S'
        self.__UpdateHelper('TemperatureStatus', TemperatureStatusCmdString, value, qualifier)

    def __MatchTemperatureStatus(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('TemperatureStatus', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        output = int(qualifier['Output'])
        plane = int(qualifier['Plane'])
        if 1 <= output <= self.OutputSize and plane in range(16):
            VideoMuteString = '{0}*{1}*{2}B'.format(plane, output, VideoMuteState[value])
            self.__SetHelper('VideoMute', VideoMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        output = int(qualifier['Output'])
        plane = int(qualifier['Plane'])
        if 1 <= output <= self.OutputSize and plane in range(16):
            VideoMuteString = '{0}*{1}B'.format(plane, output)
            self.__UpdateHelper('VideoMute', VideoMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        VideoMuteName = {
            0: 'Off',
            1: 'On',
        }

        value = VideoMuteName[int(match.group(3))]
        output = str(int(match.group(2)))
        plane = str(int(match.group(1)))
        if output != '0':
            self.WriteStatus('VideoMute', value, {'Output': output, 'Plane': plane})
        elif plane in self.PlaneList:
            outputRange = range(1, self.PlaneList[plane]['VidOut'] + 1)
            for output in outputRange:
                self.WriteStatus('VideoMute', value, {'Output': str(output), 'Plane': plane})

    def UpdateVoltageLevel(self, value, qualifier):

        VoltageLevelCmdString = '1S'
        self.__UpdateHelper('VoltageLevel', VoltageLevelCmdString, value, qualifier)

    def __MatchVoltageLevel(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('VoltageLevel', value, None)

    def SetVolume(self, value, qualifier):

        output = int(qualifier['Output'])
        plane = int(qualifier['Plane'])
        if 1 <= output <= self.OutputSize and 0 <= value <= 64 and plane in range(16):
            VolumeCmdString = '{0}*{1}*{2}V'.format(plane, output, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        output = int(qualifier['Output'])
        plane = int(qualifier['Plane'])
        if 1 <= output <= self.OutputSize and plane in range(16):
            VolumeCmdString = '{0}*{1}V'.format(plane, output)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        value = int(match.group(3))
        output = str(int(match.group(2)))
        plane = str(int(match.group(1)))
        self.WriteStatus('Volume', value, {'Output': output, 'Plane': plane})

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
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output/port number',
            '13': 'Invalid value (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

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


    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
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
