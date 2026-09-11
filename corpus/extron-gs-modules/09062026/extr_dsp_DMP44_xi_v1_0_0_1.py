from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, findall, search

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
            'GroupInputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMixpointGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters':['Group'], 'Status': {}},
            'GroupPostmixerTrim': {'Parameters':['Group'], 'Status': {}},
            'GroupPremixerGain': {'Parameters':['Group'], 'Status': {}},
            'InputGain': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'MixpointGain': {'Parameters':['Input','Output'], 'Status': {}},
            'MixpointMute': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'OutputPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'PartNumber': { 'Status': {}},
            'PremixerGain': {'Parameters':['Input'], 'Status': {}},
            'PremixerMute': {'Parameters':['Input'], 'Status': {}},
            'PresetRecall': { 'Status': {}}
        }

        self.GroupFunction = {}  # This is to maintain a global dictionary of groups and their assigned functions

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'GrpmD([0-9]{1,2})\*([0-9+-]{1,5})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(compile(b'DsG(4000[0-3])\*([0-9+-]{1,5})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'DsM(4000[0-3])\*(0|1)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'DsG2([0-3]{2})([0-3]{2})\*([0-9+-]{1,5})\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(compile(b'DsM2([0-3]{2})([0-3]{2})\*(0|1)\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(compile(b'DsM(6000[0-3])\*(0|1)\r\n'), self.__MatchOutputMute, None)
            self.AddMatchString(compile(b'DsG(6000[0-3])\*([0-9+-]{1,5})\r\n'), self.__MatchOutputAttenuation, None)
            self.AddMatchString(compile(b'(60-2041-01)\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(compile(b'DsG(6010[0-3])\*([0-9 -]{1,5})\r\n'), self.__MatchOutputPostmixerTrim, None)
            self.AddMatchString(compile(b'DsG(4010[0-3])\*([0-9+-]{1,5})\r\n'), self.__MatchPremixerGain, None)
            self.AddMatchString(compile(b'DsM(4010[0-3])\*(0|1)\r\n'), self.__MatchPremixerMute, None)
            self.AddMatchString(compile(b'E([0-9]{2})\r\n'), self.__MatchError, None)

    def UpdatePartNumber(self, value, qualifier):

        cmdString = 'n'
        self.__UpdateHelper('PartNumber', cmdString, None, None)

    def __MatchPartNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PartNumber', value, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False 
    
    def SetGroupInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -18 <= value <= 24:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupInputGain'
            self.__SetHelper('GroupInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupInputGain')

    def UpdateGroupInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupInputGain'
            self.__UpdateHelper('GroupInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupInputGain')

    def SetGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -100 <= value <= 12:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__SetHelper('GroupMixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMixpointGain')

    def UpdateGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__UpdateHelper('GroupMixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMixpointGain')

    def SetGroupMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}*{1}grpm\r\n'.format(group, ValueStateValues[value])
            self.GroupFunction[group] = 'GroupMute'
            self.__SetHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMute'
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -100 <= value <= 0:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)

    def SetGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -12 <= value <= 12:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupPostmixerTrim'
            self.__SetHelper('GroupPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupPostmixerTrim')

    def UpdateGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupPostmixerTrim'
            self.__UpdateHelper('GroupPostmixerTrim', commandString, value, qualifier)

    def SetGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -100 <= value <= 12:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupPremixerGain'
            self.__SetHelper('GroupPremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupPremixerGain')

    def UpdateGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupPremixerGain'
            self.__UpdateHelper('GroupPremixerGain', commandString, value, qualifier)

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
            elif command in ['GroupPremixerGain', 'GroupInputGain',
                             'GroupOutputAttenuation', 'GroupMixpointGain',
                             'GroupPostmixerTrim'
                             ]:
                qualifier = {'Group': group}
                value = int(match.group(2)) / 10
                self.WriteStatus(command, value, qualifier) 
    
    def SetInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4 and -18 <= value <= 24:
            level = int(value * 10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 39999, level)
            self.__SetHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = 'wG{0}AU\r\n'.format(channel + 39999)
            self.__UpdateHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        channel = str(int(match.group(1)) - 39999)
        qualifier = {'Input': channel}
        value = round((int(match.group(2))) / 10)
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 39999, ValueStateValues[value])
            self.__SetHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = 'wM{0}AU\r\n'.format(channel + 39999)
            self.__UpdateHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = str(int(match.group(1)) - 39999)
        qualifier = {'Input': channel}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetMixpointGain(self, value, qualifier):

        MixpointGainInputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }
        MixpointOutputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        if -100 <= value <= 12:
            inputValue = MixpointGainInputStateValues[Input]
            outputValue = MixpointOutputStateValues[Output]
            level = round(value * 10)
            commandString = 'wG2{0}{1}*{2:05d}AU\r\n'.format(inputValue, outputValue, level)
            self.__SetHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')

    def UpdateMixpointGain(self, value, qualifier):

        MixpointGainInputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }

        MixpointOutputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = MixpointGainInputStateValues[Input]
        outputValue = MixpointOutputStateValues[Output]
        commandString = 'wG2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('MixpointGain', commandString, value, qualifier)

    def __MatchMixpointGain(self, match, tag):

        MixpointGainInputStateNames = {
            '00': '1', '01': '2', '02': '3', '03': '4',
        }

        MixpointOutputStateNames = {
            '00': '1', '01': '2', '02': '3', '03': '4',
        }

        if 0 <= int(match.group(1).decode()) <= 36:
            Input = MixpointGainInputStateNames[match.group(1).decode()]
            Output = MixpointOutputStateNames[match.group(2).decode()]
            value = (int(match.group(3))) / 10
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('MixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        MixpointInputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }

        MixpointOutputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = MixpointInputStateValues[Input]
        outputValue = MixpointOutputStateValues[Output]
        commandString = 'wM2{0}{1}*{2}AU\r\n'.format(inputValue, outputValue, ValueStateValues[value])
        self.__SetHelper('MixpointMute', commandString, value, qualifier)

    def UpdateMixpointMute(self, value, qualifier):

        MixpointInputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }

        MixpointOutputStateValues = {
            '1': '00', '2': '01', '3': '02', '4': '03',
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = MixpointInputStateValues[Input]
        outputValue = MixpointOutputStateValues[Output]
        commandString = 'wM2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('MixpointMute', commandString, value, qualifier)

    def __MatchMixpointMute(self, match, tag):

        MixpointInputStateNames = {
            '00': '1', '01': '2', '02': '3', '03': '4',
        }

        MixpointOutputStateNames = {
            '00': '1', '01': '2', '02': '3', '03': '4',
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if 0 <= int(match.group(1).decode()) <= 36:
            Input = MixpointInputStateNames[match.group(1).decode()]
            Output = MixpointOutputStateNames[match.group(2).decode()]
            value = ValueStateValues[match.group(3).decode()]
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('MixpointMute', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 59999, ValueStateValues[value])
            self.__SetHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            commandString = 'wM{0}AU\r\n'.format(channel + 59999)
            self.__UpdateHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = str(int(match.group(1)) - 59999)
        qualifier = {'Output': channel}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetOutputPostmixerTrim(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4 and -12 <= value <= 12:
            level = round(value * 10)
            ChannelValue = channel + 60099
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(ChannelValue, level)
            self.__SetHelper('OutputPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputPostmixerTrim')

    def UpdateOutputPostmixerTrim(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            ChannelValue = channel + 60099
            commandString = 'wG{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('OutputPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputPostmixerTrim')

    def __MatchOutputPostmixerTrim(self, match, tag):

        channel = str(int(match.group(1)) - 60099)
        qualifier = {'Output': channel}
        value = (int(match.group(2))) / 10
        self.WriteStatus('OutputPostmixerTrim', value, qualifier)

    def SetOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4 and -100 <= value <= 0:
            level = round(value * 10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 59999, level)
            self.__SetHelper('OutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAttenuation')

    def UpdateOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            commandString = 'wG{0}AU\r\n'.format(channel + 59999)
            self.__UpdateHelper('OutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAttenuation')

    def __MatchOutputAttenuation(self, match, tag):

        channel = str(int(match.group(1)) - 59999)
        qualifier = {'Output': channel}
        value = (int(match.group(2))) / 10
        self.WriteStatus('OutputAttenuation', value, qualifier)

    def SetPremixerGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4 and -100 <= value <= 12:
            level = round(value * 10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 40099, level)
            self.__SetHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerGain')

    def UpdatePremixerGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = 'wG{0}AU\r\n'.format(channel + 40099)
            self.__UpdateHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerGain')

    def __MatchPremixerGain(self, match, tag):

        channel = str(int(match.group(1)) - 40099)
        qualifier = {'Input': channel}
        value = (int(match.group(2))) / 10
        self.WriteStatus('PremixerGain', value, qualifier)

    def SetPremixerMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 40099, ValueStateValues[value])
            self.__SetHelper('PremixerMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerMute')

    def UpdatePremixerMute(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = 'wM{0}AU\r\n'.format(channel + 40099)
            self.__UpdateHelper('PremixerMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerMute')

    def __MatchPremixerMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        channel = str(int(match.group(1)) - 40099)
        qualifier = {'Input': channel}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PremixerMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) <= 16:
            commandString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

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

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.VerboseDisabled:
                self.Send('w3cv\r\n')
                self.Send(commandstring)
            else:
                self.Send(commandstring)
    
    def __MatchError(self, match, tag):
        self.counter = 0


        DeviceErrorCodes = {
            '10': 'Invalid command',
            '11': 'Invalid preset',
            '12': 'Invalid port number',
            '13': 'Invalid parameter (number is out of range)',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System timed out',
            '22': 'Busy',
            '25': 'Device is not present'
        }

        if match.group(1).decode() in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode()]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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