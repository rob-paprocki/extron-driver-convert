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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'CECAudioMute': {'Parameters': ['Output'], 'Status': {}},
            'CECPower': {'Parameters': ['Output'], 'Status': {}},
            'CECShowAsActiveSource': {'Parameters': ['Output'], 'Status': {}},
            'CECVolume': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True

        self.lastInputSignalUpdate = 0
        self.lastHDCPInputStatusUpdate = 0
        self.lastHDCPOutputStatusUpdate = 0

        self.TieTimer = None

        self.CECOutputList = []

        self.matrix_tie_status = [['Untied' for _ in range(4)] for _ in range(4)]
       
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(rb'Amt0([1-4])\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Amt([01])\r\n'), self.__MatchGlobalAudioMute, None)
            self.AddMatchString(compile(b'Vmt([012])\r\n'), self.__MatchGlobalVideoMute, None)
            self.AddMatchString(compile(rb'HdcpE0([1-4])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(rb'HdcpI00\*([012]{4})\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(rb'HdcpO00\*([0-3]{2})\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Frq00 ([0-1]{4})\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(rb'Vmt([12])\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(rb'Out0([34]) Vol(\d{1,3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(rb'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Rpr[0-9]{2}\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(rb'Vgp00\*Out(\d{2})([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(rb'Vgp00\*Out(\d{2})([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'(?:Out([1-4]) In([0-4]) (All|Vid|Aud))|(?:In([0-4]) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  # Echo Mode for SSH

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.UpdateAllMatrixTie(None, None)

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def __MatchQik(self, match, tag):
    
        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(4)] for _ in range(4)]
        self.Send('w0*1*1VC\r\nw0*1*2VC\r\n')

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(4)
        for input_ in range(4):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(4)
        for input_ in range(4):
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
        for o in output_range:
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        if tag == 'Audio':
            current_output = 3
        else:
            current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        for i in input_list:
            if i != '--':
                if tag == 'Audio':
                    self.audio_status_counter += 1
                elif tag == 'Video':
                    self.video_status_counter += 1
                if i != '00':
                    if tag == 'Video':
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio'

                current_output += 1
            else:
                break
        if self.audio_status_counter == 2 and self.video_status_counter == 2:
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')
            
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Output']) <= 4:
            AudioMuteCmdString = '{0}*{1}Z'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 4:
            AudioMuteCmdString = '{0}Z'.format(qualifier['Output'])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        self.WriteStatus('AudioMute', ValueStateValues[match.group(2).decode()], {'Output': match.group(1).decode()})

    def SetCECAudioMute(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            output = qualifier['Output']
            if output not in self.CECOutputList:  # ensures to only enable once
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECAudioMuteCmdString = 'wO{}*%44%43DCEC\r'.format(output)
            self.__SetHelper('CECAudioMute', CECAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECAudioMute')

    def SetCECPower(self, value, qualifier):

        ValueStateValues = {
            'On': '%04',
            'Off': '%36'
        }

        if qualifier['Output'] in ['1', '2'] and value in ValueStateValues:
            output = qualifier['Output']
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECPowerCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECPower', CECPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECShowAsActiveSource(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            output = qualifier['Output']
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECShowAsActiveSourceCmdString = 'wO{}*\"ShowMe\"DCEC\r'.format(output)
            self.__SetHelper('CECShowAsActiveSource', CECShowAsActiveSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECShowAsActiveSource')

    def SetCECVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '%44%41',
            'Down': '%44%42'
        }

        if qualifier['Output'] in ['1', '2'] and value in ValueStateValues:
            output = qualifier['Output']
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECVolumeCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECVolume', CECVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECVolume')

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

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1*Z',
            'Off': '0*Z'
        }

        if value in ValueStateValues:
            GlobalAudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def __MatchGlobalAudioMute(self, match, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        for i in range(1, 5):
            self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output': str(i)})
            
    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1*B',
            'Video and Sync': '2*B',
            'Off': '0*B'
        }

        if value in ValueStateValues:
            GlobalVideoString = ValueStateValues[value]
            self.__SetHelper('GlobalVideoMute', GlobalVideoString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def __MatchGlobalVideoMute(self, match, qualifier):

        ValueStateValues = {
            '1': 'On',
            '2': 'Video and Sync',
            '0': 'Off'
        }

        for i in range(1, 3):
            self.WriteStatus('VideoMute', ValueStateValues[match.group(1).decode()], {'Output': str(i)})
            
    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Input']) <= 4:
            HDCPAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            HDCPAuthorizationCmdString = 'wE{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Input': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            self.__UpdateHelper('HDCPInputStatus', 'wIHDCP\r', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Connected',
            '1': 'HDCP Content',
            '2': 'No HDCP Content'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for input_ in signal:
            self.WriteStatus('HDCPInputStatus', ValueStateValues[input_], {'Input': str(inputNumber)})
            inputNumber += 1

    def UpdateHDCPOutputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 2:
            self.__UpdateHelper('HDCPOutputStatus', 'wOHDCP\r', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):      

        ValueStateValues = {
            '0': 'No monitor connected',
            '1': 'Monitor connected, HDCP not supported',
            '2': 'Monitor connected, not encrypted',
            '3': 'Monitor connected, currently encrypted'
        }

        signal = match.group(1).decode()
        outputNumber = 1
        for output in signal:
            self.WriteStatus('HDCPOutputStatus', ValueStateValues[output], {'Output': str(outputNumber)})
            outputNumber += 1

    def UpdateInputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, qualifier):

        InputList = match.group(1).decode()
        inputVal = 1
        for stat in InputList:
            value = 'Not Active' if stat == '0' else 'Active'
            self.WriteStatus('InputSignalStatus', value, {'Input': str(inputVal)})
            inputVal += 1

    def SetMatrixTieCommand(self, value, qualifier):

        Input = int(qualifier['Input'])
        Output = qualifier['Output']

        if 0 <= Input <= 4 and (Output == 'All' or 1 <= int(Output) <= 4):
            if Output == 'All':
                MatrixTieCmdString = '{0}*!'.format(Input)
                self.__SetHelper('MatrixTieCommand', MatrixTieCmdString, value, qualifier)
            else:
                MatrixTieCmdString = '{0}*{1}!'.format(Input, Output)
                self.__SetHelper('MatrixTieCommand', MatrixTieCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

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
        output = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]
        if tietype == 'Audio/Video':
            for i in range(4):
                current_tie = self.matrix_tie_status[i][output - 1]
                if i != input_ - 1 and current_tie in ['Audio', 'Audio/Video']:
                    self.matrix_tie_status[i][output - 1] = 'Untied'
                elif i == input_ - 1:
                    if output < 3:
                        self.matrix_tie_status[i][output - 1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output - 1] = 'Audio'
        elif tietype in ['Video', 'Audio']:
            for i in range(4):
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
            'All': 'Audio/Video',
        }
        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]
        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output in range(4):
                for input_ in range(4):
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
            for output in range(4):
                for input_ in range(4):
                    if input_ == new_input - 1:
                        if output < 2:
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[input_][output] = 'Audio'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')
        
    def SetRefreshMatrix(self, value, qualifier):
        self.UpdateAllMatrixTie(value, qualifier)
        
    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Video and Sync': '2',
            'Off': '0'
        }

        if value in ValueStateValues and qualifier['Output'] in ['1', '2']:
            VideoMuteCmdString = '{0}*{1}B'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            VideoMuteCmdString = '{0}B'.format(qualifier['Output'])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteName = {
            '1': 'On',
            '2': 'Video and Sync',
            '0': 'Off',
        }

        self.WriteStatus('VideoMute', VideoMuteName[match.group(2).decode()], {'Output': match.group(1).decode()})

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Output'] in ['3', '4']:
            VolumeCmdString = '{0}*{1}V'.format(qualifier['Output'], value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if qualifier['Output'] in ['3', '4']:
            VolumeCmdString = '{0}V'.format(qualifier['Output'])
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = {'Output': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, qualifier)

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
                
    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number or port number',
            '13': 'Invalid parameter',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System or command timed out',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found'
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
        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.CECOutputList.clear()
        
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
