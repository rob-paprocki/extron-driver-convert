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
        self._NumberofInputs = 4
        self._NumberofOutputs = 4
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {
            'FOX Matrix 14400': self.extr_15_97_14400,
            'FOX Matrix 3200': self.extr_15_97_3200,
            'FOX Matrix 7200': self.extr_15_97_7200,
            'FOX Matrix 320x': self.extr_15_97_320x,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'MatrixIONameCommand': {'Parameters': ['Type'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters': ['Type', 'Number'], 'Status': {}},
            'MatrixIONumberSelect': {'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'OutputTieStatusName': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'RefreshMatrixIONames': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(rb'Vgp00 Out[\d]?(\d{2})\*([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, None)
            self.AddMatchString(re.compile(rb'(Out(\d+) )?In(\d+) (RGB|All|Vid)\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(rb'Frq0{2,3}\*([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(rb'Nm([io])([0-9]{2,3}),([ \S]{1,12})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(rb'Rpr(\d+)\r\n'), self.__MatchRecallPreset, None)
            self.AddMatchString(re.compile(b'Mut([0-1]+)\r\n'), self.__MatchVideoMute, 'Query')
            self.AddMatchString(re.compile(rb'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, 'Unsolicited')
            self.AddMatchString(re.compile(b'Vmt([0-1])\r\n'), self.__MatchVideoMute, 'Global')
            self.AddMatchString(re.compile(rb'E(\d+)\r\n'), self.__MatchError, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(re.compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    @property
    def NumberofInputs(self):
        return self._NumberofInputs

    @NumberofInputs.setter
    def NumberofInputs(self, value):
        self._NumberofInputs = value

    @property
    def NumberofOutputs(self):
        return self._NumberofOutputs

    @NumberofOutputs.setter
    def NumberofOutputs(self, value):
        self._NumberofOutputs = value

    def SetPassword(self):
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
        self.UpdateAllMatrixTie(None, None)

    def __MatchQik(self, match, tag):

        self.UpdateAllMatrixTie(None, None)

    def __MatchRecallPreset(self, match, tag):

        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.Send('w0*1*1VC\r')  
        self.Send('w0*17*1VC\r')  
        if self.MatrixSize > 32:
            self.Send('w0*33*1VC\r')  
            self.Send('w0*49*1VC\r')
            self.Send('w0*65*1VC\r')
        if self.MatrixSize > 74:
            self.Send('w0*81*1VC\r')
            self.Send('w0*97*1VC\r')
            self.Send('w0*113*1VC\r')
            self.Send('w0*129*1VC\r')
        if self.MatrixSize > 144:
            self.Send('w0*145*1VC\r')
            self.Send('w0*161*1VC\r')
            self.Send('w0*177*1VC\r')
            self.Send('w0*193*1VC\r')
            self.Send('w0*209*1VC\r')
            self.Send('w0*225*1VC\r')
            self.Send('w0*241*1VC\r')
            self.Send('w0*257*1VC\r')
            self.Send('w0*273*1VC\r')
            self.Send('w0*289*1VC\r')
            self.Send('w0*305*1VC\r')

    def __MatchAllMatrixTie(self, match, tag):
        OutputOffsetLookup = {
        	'01': 1,
        	'17': 17,
        	'33': 33,
        	'49': 49,
        	'65': 65,
        	'81': 81,
        	'97': 97,
        	'13': 113,
        	'29': 129,
        	'45': 145,
        	'61': 161,
        	'77': 177,
        	'93': 193,
        	'09': 209,
        	'25': 225,
        	'41': 241,
        	'57': 257,
        	'73': 273,
        	'89': 289,
        	'05': 305
        }

        outputOffset = OutputOffsetLookup[match.group(1).decode()]
        inputList = match.group(2).decode().split()
        for output, input_ in enumerate(inputList):
            if input_ == '--':  
                break  

            input_ = str(int(input_))  
            output = output + outputOffset  
            self.WriteStatus('OutputTieStatus', input_, {'Output': str(output)})  
            self.OutputTieStatusList[output - 1] = input_  
            matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self._NumberofOutputs)})  
            if matrixIONameStatus:  
                if input_ == '0':  
                    inputName = 'Untied'  
                else:
                    inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': input_})  
                    inputName = 'Untied' if not inputName else inputName  
                self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output)})  
 
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ExecutiveModeCmdString = '{0}X'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        GlobalVideoMuteCmdString = '{0}*B'.format(ValueStateValues[value])
        self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.MatrixSize:
            InputSignalStatusCmdString = '0LS'
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Input')
       

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        for input_, value in enumerate(match.group(1).decode()):
            self.WriteStatus('InputSignalStatus', ValueStateValues[value], {'Input': str(input_ + 1)})

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input': 'NI',
            'Output': 'NO'
        }

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 1 <= len(name) <= 12 and qualifier['Type'] in TypeStates:
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[qualifier['Type']])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        number = str(int(match.group(2).decode()))
        value = match.group(3).decode()
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})
        if type_ == 'Input':  
            for x in range(1, self.MatrixSize + 1):
                if self.ReadStatus('OutputTieStatus', {'Output': str(x)}) == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x)})
    
    def SetRefreshMatrixIONames(self, value, qualifier):

        self.UpdateMatrixIONames(None, None)

    def UpdateMatrixIONames(self, value, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '17': 'Timeout (caused only by direct write of global presets)',
            '21': 'Invalid room number',
            '24': 'Privileges violation'
        }
        prevTime = 0
        for i in range(1, self._NumberofInputs + 1):
            if i <= self.MatrixSize:                
                res = self.SendAndWait('w{0}NI\r'.format(i), 0.2, deliTag='\n')
                if res:
                    if res[0] == 'N':
                        refIndex = res.find(',')
                        num = int(res[3:6]) if res[5] != ',' else int(res[3:5])
                        value = res[refIndex + 1:-2].strip()
                        self.WriteStatus('MatrixIONameStatus', value, {'Type': 'Input', 'Number': str(num)})
                    else:
                        if res[1:3] in DEVICE_ERROR_CODES:
                            self.Error(['Matrix Input {0} Name: {1}'.format(i, DEVICE_ERROR_CODES[res[1:3]])])
                        else:
                            self.Error(['Matrix Input {0} Name: Unrecognized error code: E{1}'.format(i, res[1:3])])
                else:
                    self.Error(['Matrix Input {0} Name: Invalid/unexpected response'.format(i)])
            else:
                self.Discard('Invalid Command for UpdateMatrixIONames')
        prevTime = 0
        for i in range(1, self._NumberofOutputs + 1):
            if i <= self.MatrixSize:               
                res = self.SendAndWait('w{0}NO\r'.format(i), 0.2, deliTag='\n')
                if res:
                    if res[0] == 'N':
                        refIndex = res.find(',')
                        num = int(res[3:6]) if res[5] != ',' else int(res[3:5])
                        value = res[refIndex + 1:-2].strip()
                        self.WriteStatus('MatrixIONameStatus', value, {'Type': 'Output', 'Number': str(num)})
                    else:
                        if res[1:3] in DEVICE_ERROR_CODES:
                            self.Error(['Matrix Output {0} Name: {1}'.format(i, DEVICE_ERROR_CODES[res[1:3]])])
                        else:
                            self.Error(['Matrix Output {0} Name: Unrecognized error code: E{1}'.format(i, res[1:3])])
                else:
                    self.Error(['Matrix Output {0} Name: Invalid/unexpected response'.format(i)])
            else:
                self.Discard('Invalid Command for UpdateMatrixIONames')

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']
        if 0 <= int(input_) <= self.MatrixSize and output == 'All':
            MatrixTieCommandCmdString = '{0}*!'.format(input_)
        elif 0 <= int(input_) <= self.MatrixSize and 1 <= int(output) <= self.MatrixSize:
            MatrixTieCommandCmdString = '{0}*{1}!'.format(input_, output)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')
            return
        self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)

    def __MatchOutputTieStatus(self, match, tag):

        if match.group(1):  
            output = int(match.group(2).decode())
            input_ = str(int(match.group(3).decode()))
            self.OutputTieStatusList[output - 1] = input_  
            self.WriteStatus('OutputTieStatus', input_, {'Output': str(output)})  
            matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self._NumberofOutputs)})  
            if matrixIONameStatus:  
                if input_ == '0':  
                    inputName = 'Untied'  
                else:
                    inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': input_})  
                    inputName = 'Untied' if not inputName else inputName  
                self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output)})  
        else:  
            input_ = str(int(match.group(3).decode()))
            for output in range(self.MatrixSize):  
                self.OutputTieStatusList[output] = input_  
                self.WriteStatus('OutputTieStatus', input_, {'Output': str(output + 1)})  
                matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self._NumberofOutputs)})  
                if matrixIONameStatus:  
                    if input_ == '0':  
                        inputName = 'Untied'  
                    else:
                        inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': input_})  
                        inputName = 'Untied' if not inputName else inputName  
                    self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output + 1)})  

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= self.MaxPreset:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= self.MaxPreset:
            PresetSaveCmdString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        ValueStateValues = {
            '1 - 16': 'w0*1*1VC\r',
            '17 - 32': 'w0*17*1VC\r',
            '33 - 48': 'w0*33*1VC\r',
            '49 - 64': 'w0*49*1VC\r',
            '65 - 72': 'w0*65*1VC\r',
            '65 - 80': 'w0*65*1VC\r',
            '81 - 96': 'w0*81*1VC\r',
            '97 - 112': 'w0*97*1VC\r',
            '113 - 128': 'w0*113*1VC\r',
            '129 - 144': 'w0*129*1VC\r',
            '145 - 160': 'w0*145*1VC\r',
            '161 - 176': 'w0*161*1VC\r',
            '177 - 192': 'w0*177*1VC\r',
            '193 - 208': 'w0*193*1VC\r',
            '209 - 224': 'w0*209*1VC\r',
            '225 - 240': 'w0*225*1VC\r',
            '241 - 256': 'w0*241*1VC\r',
            '257 - 272': 'w0*257*1VC\r',
            '273 - 288': 'w0*273*1VC\r',
            '289 - 304': 'w0*289*1VC\r',
            '305 - 320': 'w0*305*1VC\r'
        }

        if value == 'All':
            self.UpdateAllMatrixTie(None, None)
        else:
            self.__SetHelper('RefreshMatrix', ValueStateValues[value], value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Output']) <= self.MatrixSize:
            VideoMuteCmdString = '{0}*{1}B'.format(qualifier['Output'], VideoMuteState[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.MatrixSize:
            VideoMuteCmdString = 'wVM\r'
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Output')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if tag == 'Query':
            for output, value in enumerate(match.group(1).decode()):
                self.WriteStatus('VideoMute', ValueStateValues[value], {'Output': str(output + 1)})           
        elif tag == 'Unsolicited':
            self.WriteStatus('VideoMute', ValueStateValues[match.group(2).decode()], {'Output': str(int(match.group(1).decode()))})
        elif tag == 'Global':
            for output in range(self.MatrixSize):
                self.WriteStatus('VideoMute', ValueStateValues[match.group(1).decode()], {'Output': str(output + 1)})

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
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '17': 'Timeout (caused only by direct write of global presets)',
            '21': 'Invalid room number',
            '24': 'Privileges violation'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E' + match.group(1).decode()])

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
        
    def extr_15_97_3200(self):
        self.MatrixSize = 32
        self.MaxPreset = 32
        self.OutputTieStatusList = ['Initial' for i in range(self.MatrixSize)]

    def extr_15_97_7200(self):
        self.MatrixSize = 72
        self.MaxPreset = 64
        self.OutputTieStatusList = ['Initial' for i in range(self.MatrixSize)]

    def extr_15_97_14400(self):
        self.MatrixSize = 144
        self.MaxPreset = 64
        self.OutputTieStatusList = ['Initial' for i in range(self.MatrixSize)]

    def extr_15_97_320x(self):
        self.MatrixSize = 320
        self.MaxPreset = 64
        self.OutputTieStatusList = ['Initial' for i in range(self.MatrixSize)]
        
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

