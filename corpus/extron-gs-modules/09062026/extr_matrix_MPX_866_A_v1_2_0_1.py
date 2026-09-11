from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, match, search
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
        self.Models = {}
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputFormat': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Tie Type', 'Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True

        self.InputSize = 14
        self.OutputSize = 12
        self.matrix_tie_status = []

        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Out(\d) Vol(\d{2})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'In0+ ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Amt(\d+)\*([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Rpr(\d+)\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Vgp00 Out(\d{2}) ([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vgp00 Out(\d{2}) ([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'Vmt[0-1]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Amt[0-1]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Mut([0-3]+)\r\n'), self.__MatchMute, None)
            self.AddMatchString(compile(b'Typ(\d+)\*(1|2)\r\n'), self.__MatchInputFormat, None)

    def SetPassword(self):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword()

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0
        self.SetVerbose(None, None)

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])
        self.SetVerbose(None, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.SetRefreshMatrix(None, None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.__UpdateHelper('Mute', 'wvm\r', value, qualifier)

    def __MatchMute(self, match, tag):
        stat = match.group(1).decode()
        output_ = 1
        for i in stat:
            if i == '0':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(output_)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output_)})
            elif i == '1':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(output_)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output_)})
            elif i == '2':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output_)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output_)})
            elif i == '3':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output_)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output_)})
            output_ += 1

    def __MatchQik(self, match, tag):

        self.SetRefreshMatrix(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.__UpdateHelper('RefreshMatrix', 'w0*1*1VC\r\nw0*1*2VC\r\n', value, qualifier)

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def InputTieStatusHelper(self, tie, output_=None):
        if tie == 'Individual':
            output_range = range(output_ - 1, output_)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output_ in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output_], {'Input': str(input_ + 1), 'Output': str(output_ + 1)})

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def OutputTieStatusHelper(self, tie, output_=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output_ - 1, output_)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output_ in output_range:

                tietype = self.matrix_tie_status[input_][output_]
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output_ + 1), 'Tie Type': tie_type})
                    AudioList.add(output_)
                    VideoList.add(output_)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output_ + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output_ + 1), 'Tie Type': 'Audio'})
                    AudioList.add(output_)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output_ + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output_ + 1), 'Tie Type': 'Video'})
                    VideoList.add(output_)

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

        opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

        for i in input_list:
            if i != '--':
                if i != '00':
                    if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag
                current_output += 1
        if tag == 'Audio':
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
                        'Off': '0',
                        'On': '1',
                        }

        AudioChannels = {
            'Min': 1,
            'Max': 6
            }

        channel = int(qualifier['Output'])
        if channel < AudioChannels['Min'] or channel > AudioChannels['Max']:
            self.Discard('Invalid Command for SetAudioMute')
        else:
            self.__SetHelper('AudioMute', '{0}*{1}z'.format(channel, AudioMuteState[value]), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioChannels = {
            'Min': 1,
            'Max': 6
            }

        channel = int(qualifier['Output'])
        if channel < AudioChannels['Min'] or channel > AudioChannels['Max']:
            self.Discard('Invalid Command for UpdateAudioMute')
        else:
            self.__UpdateHelper('AudioMute', '{0}z'.format(channel), value, qualifier)

    def __MatchAudioMute(self, match, qualifier):
        AudioMuteName = {
                        b'0': 'Off',
                        b'1': 'On',
                        }
        self.WriteStatus('AudioMute', AudioMuteName[match.group(2)], {'Output': str(int(match.group(1)))})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
                        'Mode 1': '1',
                        'Mode 2': '2',
                        'Off': '0'
                        }
        self.__SetHelper('ExecutiveMode', '{0}x'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'x', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
                        b'1': 'Mode 1',
                        b'2': 'Mode 2',
                        b'0': 'Off',
                        }

        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1)], None)

    def SetGlobalAudioMute(self, value, qualifier):
        AudioMuteState = {
                        'Off': '0',
                        'On': '1'
                        }
        self.__SetHelper('GlobalAudioMute', '{0}*z'.format(AudioMuteState[value]), value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):
        VideoMuteState = {
                        'Off': '0',
                        'On': '1',
                        }
        self.__SetHelper('GlobalVideoMute', '{0}*b'.format(VideoMuteState[value]), value, qualifier)

    def SetInputFormat(self, value, qualifier):

        InputFormatState = {
                        'Composite Video': '1',
                        'S-Video': '2',
                        }

        VideoChannels = {
            'Min': 11,
            'Max': 14
            }

        channel = int(qualifier['Input'])
        if channel < VideoChannels['Min'] or channel > VideoChannels['Max']:
            self.Discard('Invalid Command for SetInputFormat')
        else:
            self.__SetHelper('InputFormat', '{0}*{1}\\'.format(channel, InputFormatState[value]), value, qualifier)

    def UpdateInputFormat(self, value, qualifier):

        VideoChannels = {
            'Min': 11,
            'Max': 14
            }

        channel = int(qualifier['Input'])
        if channel < VideoChannels['Min'] or channel > VideoChannels['Max']:
            self.Discard('Invalid Command for UpdateInputFormat')
        else:
            self.__UpdateHelper('InputFormat', '{0}\\'.format(channel), value, qualifier)

    def __MatchInputFormat(self, match, qualifier):
        InputFormatName = {
                        b'1': 'Composite Video',
                        b'2': 'S-Video',
                        }
        self.WriteStatus('InputFormat', InputFormatName[match.group(2)], {'Input': str(int(match.group(1)))})

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatus = {
            '1': 'Active',
            '0': 'Not Active'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for inputVal in signal:
            self.WriteStatus('InputSignalStatus', InputSignalStatus[inputVal], {'Input': str(inputNumber)})
            inputNumber += 1

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio': '$',  
            'Video': '&', 
            'Audio/Video': '!'
            }

        input_ = int(qualifier['Input'])
        output_ = qualifier['Output']
        tieType = qualifier['Tie Type']

        if output_ == 'All':
            output_ = ''
        elif int(output_) < 0 or int(output_) > 12:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif input_ < 0 or input_ > 14:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif input_ <= 8 and int(output_) >= 7 and input_ != 0:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif input_ in range(9,15) and int(output_) in range(1,7) and tieType in ['Video'] and input_ != 0:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif input_ in range(9,15) and int(output_)in range(7,13) and tieType in ['Audio'] and input_ != 0:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.__SetHelper('MatrixTieCommand', '{0}*{1}{2}'.format(input_, output_, TieTypeValues[tieType]), input_, qualifier)

    def __MatchOutputTieStatus(self, match, qualifier):
        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video',
        }
        output_ = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output_-1]
                if i != input_-1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output_-1] = 'Untied'
                elif i == input_-1:
                    self.matrix_tie_status[i][output_-1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output_-1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_-1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output_-1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output_-1] = tietype
                elif input_ == 0 or i != input_-1:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output_-1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output_-1] = opTag

        self.OutputTieStatusHelper('Individual', output_)
        self.InputTieStatusHelper('Individual', output_)

    def __MatchAllTie(self, match, qualifier):

        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video',
        }

        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]

        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output_ in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input-1:
                        if self.matrix_tie_status[input_][output_] == op_tie_type:
                            self.matrix_tie_status[input_][output_] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[input_][output_] = tietype
                    else:
                        if self.matrix_tie_status[input_][output_] == 'Audio/Video':
                            self.matrix_tie_status[input_][output_] = op_tie_type
                        elif self.matrix_tie_status[input_][output_] != op_tie_type:
                            self.matrix_tie_status[input_][output_] = 'Untied'
        elif tietype == 'Audio/Video':
            for output_ in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input-1:
                        self.matrix_tie_status[input_][output_] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[input_][output_] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        value = int(value)
        if 0 < value < 33:   
            self.__SetHelper('PresetRecall', '{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        value = int(value)
        if 0 < value < 33:   
            self.__SetHelper('PresetSave', '{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetVideoMute(self, value, qualifier):

        VideoMuteState={
                        'Off':'0',
                        'On':'1',
                        }

        VideoChannels = {
            'Min' : 1,
            'Max' : 12
            }

        channel = int(qualifier['Output'])
        if VideoChannels['Min'] <= channel <= VideoChannels['Max']:
            self.__SetHelper('VideoMute', '{0}*{1}b'.format(channel, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoChannels = {
            'Min' : 1,
            'Max' : 12
            }

        channel = int(qualifier['Output'])
        if VideoChannels['Min'] <= channel <= VideoChannels['Max']:
            self.__UpdateHelper('VideoMute', '{0}b'.format(channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteName={
                        b'0':'Off',
                        b'1':'On',
                        }
        self.WriteStatus('VideoMute', VideoMuteName[match.group(2)], {'Output':str(int(match.group(1)))})

    def SetVolume(self, value, qualifier):

        AudioChannels = {
            'Min' : 1,
            'Max' : 6
            }

        channel = int(qualifier['Output'])
        if channel < AudioChannels['Min'] or channel > AudioChannels['Max']:
            self.Discard('Invalid Command for SetVolume')
        elif value < 0 or value > 64:
            self.Discard('Invalid Command for SetVolume') 
        else:
            self.__SetHelper('Volume', '{0}*{1}v'.format(channel, value), value, qualifier)

    def UpdateVolume(self, value, qualifier):

        AudioChannels = {
            'Min' : 1,
            'Max' : 6
            }

        channel = int(qualifier['Output'])
        if channel < AudioChannels['Min'] or channel > AudioChannels['Max']:
            self.Discard('Invalid Command for UpdateVolume')
        else:
            self.__UpdateHelper('Volume', '{0}v'.format(channel), value, qualifier)

    def __MatchVolume(self, match, fncN):

        self.WriteStatus('Volume', int(match.group(2)), {'Output':str(int(match.group(1)))})

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
    
        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

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
            '01' : 'Invalid input number (too large)',
            '10' : 'Invalid Command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid value (out of range)',
            '14' : 'Command not available for this configuration',
            '17' : 'System timed out',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '27' : 'Invalid event number',
            '28' : 'Bad filename or file not found',
            '30' : 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31' : 'Attempt to break port pass-through when it has not been set',
            '32' : 'Incorrect V-chip password'
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: '+ match.group(0).decode()]) 


    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Needed'
        self.PasswdPromptCount = 0
        self.VerboseDisabled = True

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
            print(command, 'does not exist in the module')

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
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}                

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