from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re
from struct import pack

class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BankSelect': { 'Status': {}},
            'InputChannelLevel': {'Parameters':['Input'], 'Status': {}},
            'InputChannelMute': {'Parameters':['Input'], 'Status': {}},
            'InputGroupLevel': {'Parameters':['Group'], 'Status': {}},
            'MatrixCrosspointGroupLevel': {'Parameters':['Group'], 'Status': {}},
            'MatrixCrosspointLevel': {'Parameters':['Input','Output'], 'Status': {}},
            'MatrixCrosspointMute': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputChannelLevel': {'Parameters':['Output'], 'Status': {}},
            'OutputChannelMute': {'Parameters':['Output'], 'Status': {}},
            'OutputGroupLevel': {'Parameters':['Group'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Switch': {'Parameters':['Switch'], 'Status': {}},
        }

    def SetBankSelect(self, value, qualifier): 

        state = {
            '1': 0,
            '2': 1
        }

        CmdString = pack('>BBB', 0xB0, 0x00, state[value])
        self.__SetHelper('BankSelect', CmdString, value, qualifier)

    def SetInputChannelLevel(self, value, qualifier): 

        LevelConstraints = {
           'Max': 127,
           'Min': 0
        }

        InputConstraints = {
            'Max' : 16,
            'Min' : 1
        }

        InputNum = int(qualifier['Input'])
        if LevelConstraints['Min'] <= int(value) <= LevelConstraints['Max'] \
                and InputConstraints['Min'] <= InputNum <= InputConstraints['Max']:
            CmdString = pack('>BBBBBBB', 0xB0, 0x63,(int(InputNum)-1), 0x62, 0x17, 0x06, value)
            self.__SetHelper('InputChannelLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputChannelLevel')

    def SetInputChannelMute(self, value, qualifier): 

        StateValues = {
            'On' : 127,
            'Off' : 1
        }

        InputConstraints = {
            'Max' : 16,
            'Min' : 1,
        }

        InputNum = int(qualifier['Input'])
        if InputConstraints['Min'] <= InputNum <= InputConstraints['Max']: 
            CmdString = pack('>BBB', 0x90, (int(InputNum)-1), StateValues[value])
            self.__SetHelper('InputChannelMute', CmdString, value, qualifier)      
        else:
            self.Discard('Invalid Command for SetInputChannelMute')

    def SetInputGroupLevel(self, value, qualifier): 

        GroupLevelConstraints = {
           'Max': 127,
           'Min': 0
        }

        InputConstraints = {
            'Max' : 8,
            'Min' : 1,
        }
        
        InputNum = int(qualifier['Group'])
        if InputConstraints['Min'] <= InputNum <= InputConstraints['Max'] \
                and GroupLevelConstraints['Min'] <= value <= GroupLevelConstraints['Max']:
            CmdString = pack('>BBBBBBB', 0xB0, 0x63, (int(InputNum)-1), 0x62, 0x18, 0x06, value)
            self.__SetHelper('InputGroupLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGroupLevel')

    def SetMatrixCrosspointGroupLevel(self, value, qualifier): 

        GroupLevelConstraints = {
            'Max': 127,
            'Min': 0
        }

        InputConstraints = {
            'Max' : 16,
            'Min' : 1
        }
        
        InputNum = int(qualifier['Group'])
        if InputConstraints['Min'] <= InputNum <= InputConstraints['Max'] \
                and GroupLevelConstraints['Min'] <= int(value) <= GroupLevelConstraints['Max']:
            CmdString = pack('>BBBBBBB', 0xB0, 0x63, (int(InputNum)-1), 0x62, 0x1C, 0x06, value)
            self.__SetHelper('MatrixCrosspointGroupLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixCrosspointGroupLevel')  

    def SetMatrixCrosspointLevel(self, value, qualifier): 

        InputConstraints = {
            'Max' : 16,
            'Min' : 1,
        }

        OutputConstraints = {
            'Max' : 16,
            'Min' : 1,
        }
        
        LevelConstraints = {
            'Max': 127,
            'Min': 0
        }

        InputNum = int(qualifier['Input'])
        OutputNum = int(qualifier['Output'])

        if InputConstraints['Min'] <= InputNum <= InputConstraints['Max'] \
                and OutputConstraints['Min'] <= OutputNum <= OutputConstraints['Max'] \
                and LevelConstraints['Min'] <= int(value) <= LevelConstraints['Max']:
            CmdString = pack('>BBBBBBB', 0xB0, 0x63, (int(OutputNum)-1), 0x62, (int(InputNum)-1), 0x06, value)
            self.__SetHelper('MatrixCrosspointLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixCrosspointLevel')  

    def SetMatrixCrosspointMute(self, value, qualifier): 

        StateValues = {
            'On' : 127, 
            'Off' : 1, 
        }

        InputConstraints = {
            'Max' : 16,
            'Min' : 1,
        }

        OutputConstraints = {
            'Max' : 16,
            'Min' : 1,
        }

        InputNum = int(qualifier['Input'])
        OutputNum = int(qualifier['Output'])

        if InputConstraints['Min'] <= InputNum <= InputConstraints['Max'] \
                and OutputConstraints['Min'] <= OutputNum <= OutputConstraints['Max']:
            CmdString = pack('>BBBBBBB', 0xB0, 0x63, (int(OutputNum)-1), 0x62, (int(InputNum)+63), 0x06, StateValues[value])
            self.__SetHelper('MatrixCrosspointMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixCrosspointMute')

    def SetOutputChannelLevel(self, value, qualifier): 

        LevelConstraints = {
            'Max': 127,
            'Min': 0
        }

        OutputConstraints = {
            'Max' : 16,
            'Min' : 1,
        }
        
        OutputNum = int(qualifier['Output'])
        if OutputConstraints['Min'] <= OutputNum <= OutputConstraints['Max'] \
                and LevelConstraints['Min'] <= int(value) <= LevelConstraints['Max']:
            CmdString = pack('>BBBBBBB', 0xB0, 0x63, (int(OutputNum)-1), 0x62, 0x1B, 0x06, value)
            self.__SetHelper('OutputChannelLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputChannelLevel')

    def SetOutputChannelMute(self, value, qualifier): 

        StateValues = {
            'On' : 127, 
            'Off' : 1, 
        }

        OutputConstraints = {
            'Max' : 16,
            'Min' : 1,
        }

        OutputNum = int(qualifier['Output'])
        if OutputConstraints['Min'] <= OutputNum <= OutputConstraints['Max']:
            CmdString = pack('>BBB', 0x90, (int(OutputNum)+31), StateValues[value])
            self.__SetHelper('OutputChannelMute', CmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetOutputChannelMute')

    def SetOutputGroupLevel(self, value, qualifier): 

        LevelConstraints = {
            'Max': 127,
            'Min': 0
        }

        OutputConstraints = {
            'Max' : 8,
            'Min' : 1,
        }

        OutputNum = int(qualifier['Group'])
        if OutputConstraints['Min'] <= OutputNum <= OutputConstraints['Max'] \
                and LevelConstraints['Min'] <= int(value) <= LevelConstraints['Max']:
            CmdString = pack('>BBBBBBB', 0xB0, 0x63, (int(OutputNum)-1), 0x62, 0x19, 0x06, value)
            self.__SetHelper('OutputGroupLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGroupLevel')  

    def SetPresetRecall(self, value, qualifier): 

        if 0 <= int(value) <= 250:
            CmdString = pack('>BB', 0xC0, (int(value)-1))
            self.__SetHelper('PresetRecall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetSwitch(self, value, qualifier): 

        StateValues = {
            'On'  : 127, #0x7F,  
            'Off' : 1, #0x01, 
        }

        Constraints = {
            'Max' : 16,
            'Min' : 1,
        }

        SwitchNum = int(qualifier['Switch'])
        if Constraints['Min'] <= SwitchNum <= Constraints['Max']:
            CmdString = pack('>BBB', 0x90, int(SwitchNum)+63, StateValues[value])
            self.__SetHelper('Switch', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitch')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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

class DeviceEthernetClass:
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
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CrossPointGain': {'Parameters':['Input Select','Output Select'], 'Status': {}},
            'CrossPointGroupGain': {'Parameters':['Matrix Group Select'], 'Status': {}},
            'CrossPointMute': {'Parameters':['Input Select','Output Select'], 'Status': {}},
            'InputGain': {'Parameters':['Input Select'], 'Status': {}},
            'InputGroupGain': {'Parameters':['Input Group Select'], 'Status': {}},
            'InputMute': {'Parameters':['Input Select'], 'Status': {}},
            'OutputGain': {'Parameters':['Output Select'], 'Status': {}},
            'OutputGroupGain': {'Parameters':['Output Group Select'], 'Status': {}},
            'OutputMute': {'Parameters':['Output Select'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

    def __MatchPassword(self, match, qualifier):

        self.SetPassword( None, None)

    def SetPassword(self, value, qualifier):

        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetCrossPointGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -40,
            'Max' : 0
        }

        inputS = int(qualifier['Input Select'])
        outputS = int(qualifier['Output Select'])

        if (1 <= inputS <= 16 and 1 <= outputS <= 16) and  ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CrossPointGainCmdString = 'SET XPGAIN {0} {1} {2}\r'.format(inputS, outputS, value)
            self.__SetHelper('CrossPointGain', CrossPointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossPointGain')

    def UpdateCrossPointGain(self, value, qualifier):

        inputS = int(qualifier['Input Select'])
        outputS = int(qualifier['Output Select'])

        if 1 <= inputS <= 16 and 1 <= outputS <= 16:
            CrossPointGainCmdString = 'GET XPGAIN {0} {1}\r'.format(inputS, outputS)
            res = self.__UpdateHelper('CrossPointGain', CrossPointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('CrossPointGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Cross Point Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrossPointGain')

    def SetCrossPointGroupGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -64,
            'Max' : 0
        }

        groupS = int(qualifier['Matrix Group Select'])

        if 1 <= groupS <= 16 and  ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CrossPointGroupGainCmdString = 'SET XPGROUPGAIN {0} {1}\r'.format(groupS, value)
            self.__SetHelper('CrossPointGroupGain', CrossPointGroupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossPointGroupGain')

    def UpdateCrossPointGroupGain(self, value, qualifier):

        groupS = int(qualifier['Matrix Group Select'])

        if 1 <= groupS <= 16:
            CrossPointGroupGainCmdString = 'GET XPGROUPGAIN {0}\r'.format(groupS)
            res = self.__UpdateHelper('CrossPointGroupGain', CrossPointGroupGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('CrossPointGroupGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Cross Point Group Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrossPointGroupGain')

    def SetCrossPointMute(self, value, qualifier):

        inputS = int(qualifier['Input Select'])
        outputS = int(qualifier['Output Select'])
        
        if 1 <= inputS <= 16 and 1 <= outputS <= 16:
            CrossPointMuteCmdString = 'SET XPMUTE {0} {1} {2}\r'.format(inputS, outputS, value)
            self.__SetHelper('CrossPointMute', CrossPointMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossPointMute')

    def UpdateCrossPointMute(self, value, qualifier):

        responseValue = {
            'On'    :   'On',
            'Off'   :   'Off'
        }

        inputS = int(qualifier['Input Select'])
        outputS = int(qualifier['Output Select'])

        CrossPointMuteCmdString = 'GET XPMUTE {0} {1}\r'.format(inputS, outputS)
        res = self.__UpdateHelper('CrossPointMute', CrossPointMuteCmdString, value, qualifier)
        if res:
            try:
                value = responseValue[res[:-1]]
                self.WriteStatus('CrossPointMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Cross Point Mute: Invalid/unexpected response'])

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -59,
            'Max' : 5
        }

        inputS = int(qualifier['Input Select'])

        if 1 <= inputS <= 16 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGainCmdString = 'SET IPGAIN {0} {1}\r'.format(inputS, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        inputS = int(qualifier['Input Select'])

        InputGainCmdString = 'GET IPGAIN {0}\r'.format(inputS)
        res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        if res:
            try:
                value = int(float(res))
                self.WriteStatus('InputGain', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Input Gain: Invalid/unexpected response'])

    def SetInputGroupGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -64,
            'Max' : 0
        }
        
        inputG = int(qualifier['Input Group Select'])

        if 1<= inputG <= 8 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGroupGainCmdString = 'SET IPGROUPGAIN {0} {1}\r'.format(inputG, value)
            self.__SetHelper('InputGroupGain', InputGroupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGroupGain')

    def UpdateInputGroupGain(self, value, qualifier):
        
        inputG = int(qualifier['Input Group Select'])

        if 1<= inputG <= 8:
            InputGroupGainCmdString = 'GET IPGROUPGAIN {0}\r'.format(inputG)
            res = self.__UpdateHelper('InputGroupGain', InputGroupGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('InputGroupGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Input Group Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputGroupGain')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'On', 
            'Off' : 'Off'
        }

        inputS = int(qualifier['Input Select'])
        if 1 <= inputS <= 16:
            InputMuteCmdString = 'SET IPMUTE {0} {1}\r'.format(inputS,ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):
        
        responseValue = {
            'On'    :   'On',
            'Off'   :   'Off'
        }

        inputS = int(qualifier['Input Select'])
        if 1 <= inputS <= 16:
            InputMuteCmdString = 'GET IPMUTE {0}\r'.format(inputS)
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                try:
                    value = responseValue[res[:-1]]
                    self.WriteStatus('InputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -59,
            'Max' : 5
        }

        outputS = int(qualifier['Output Select'])

        if 1<= outputS <= 16 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputGainCmdString = 'SET OPGAIN {0} {1}\r'.format(outputS,value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        outputS = int(qualifier['Output Select'])

        if 1<= outputS <= 16:
            OutputGainCmdString = 'GET OPGAIN {0}\r'.format(outputS)
            res = self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('OutputGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Output Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def SetOutputGroupGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -64,
            'Max' : 0
        }

        outputG = int(qualifier['Output Group Select'])

        if 1 <= outputG <= 8 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputGroupGainCmdString = 'SET OPGROUPGAIN {0} {1}\r'.format(outputG,value)
            self.__SetHelper('OutputGroupGain', OutputGroupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGroupGain')

    def UpdateOutputGroupGain(self, value, qualifier):

        outputG = int(qualifier['Output Group Select'])
        OutputGroupGainCmdString = 'GET OPGROUPGAIN {0}\r'.format(outputG)
        res = self.__UpdateHelper('OutputGroupGain', OutputGroupGainCmdString, value, qualifier)
        if res:
            try:
                value = int(float(res))
                self.WriteStatus('OutputGroupGain', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Output Group Gain: Invalid/unexpected response'])

    def SetOutputMute(self, value, qualifier):

        outputS = int(qualifier['Output Select'])

        if 1 <= outputS <= 16:
            OutputMuteCmdString = 'SET OPMUTE {0} {1}\r'.format(outputS, value)
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):
        
        responseValue = {
            'On'    :   'On',
            'Off'   :   'Off'
        }

        outputS = int(qualifier['Output Select'])

        OutputMuteCmdString = 'GET OPMUTE {0}\r'.format(outputS)
        res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        if res:
            try:
                value = responseValue[res[:-1]]
                self.WriteStatus('OutputMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Output Mute: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 250:
            PresetRecallCmdString = 'SET PRESET {0}\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'GET PRESET\r'
        res = self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        if res:
            try:
                value = str(int(float(res)))
                self.WriteStatus('PresetRecall', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Preset Recall: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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