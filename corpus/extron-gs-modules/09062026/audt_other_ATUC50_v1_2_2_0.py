from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, search

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
            'AuxLevel': { 'Status': {}},
            'AuxNominalLevel': { 'Status': {}},
            'DelegateTalkControlCommand': {'Parameters': ['DU', 'Unit Type'], 'Status': {}},
            'DelegateTalkControlStatus': {'Parameters': ['DU'], 'Status': {}},
            'Firmware': { 'Status': {}},
            'InterpretationReturnLevel': {'Parameters': ['Input'], 'Status': {}},
            'InterpretationReturnNominalLevel': {'Parameters': ['Input'], 'Status': {}},
            'MicLineGain': {'Parameters': ['Input'], 'Status': {}},
            'MicLineLevel': {'Parameters': ['Input'], 'Status': {}},
            'MicLineType': {'Parameters': ['Input'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Output'], 'Status': {}},
            'OutputSource': {'Parameters': ['Output'], 'Status': {}},
            'PresetBankName': {'Parameters': ['Number'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'RecordingElapsedTime': { 'Status': {}},
            'RecordingRemainingTime': { 'Status': {}},
            'SoundRecording': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'gxinp 0000 00 NC ([\d,]+) \r'), self.__MatchAuxLevel, None)

            du_talk_status_regex = br'gtalk 0000 00 (?:NC|CS|CM|CE) (\d{1,8}),(1,0|0,0|0,1),(?:\d|10),[0-4](?:,[01] | )\r'

            self.AddMatchString(compile(du_talk_status_regex), self.__MatchDelegateTalkControlStatus, None)
            self.AddMatchString(compile(b'gvers 0000 00 NC ([\d.]+) \r'), self.__MatchFirmware, None)
            self.AddMatchString(compile(b'giinp 0000 00 NC ([\d,]+) \r'), self.__MatchInterpretationReturn, None)
            self.AddMatchString(compile(b'gminp 0000 00 NC ([\d,]+) \r'), self.__MatchMicLine, None)
            self.AddMatchString(compile(b'gaout 0000 00 CS 1,(?P<Level>\d+),(?P<Source>\d+)(?P<String>[,.\d]+ \r)'), self.__MatchOutput, '1')
            self.AddMatchString(compile(b'gaout 0000 00 CM 2,(?P<Level>\d+),(?P<Source>\d+) \r'), self.__MatchOutput, '2')
            self.AddMatchString(compile(b'gaout 0000 00 CM 3,(?P<Level>\d+),(?P<Source>\d+) \r'), self.__MatchOutput, '3')
            self.AddMatchString(compile(b'gaout 0000 00 CE 4,(?P<Level>\d+),(?P<Source>\d+) \r'), self.__MatchOutput, '4')
            self.AddMatchString(compile(b'recst 0000 00 (?:NC|CS|CM|CE) ([012]),(\d{6}),(\d{6}) \r'), self.__MatchSoundRecording, None)
            self.AddMatchString(compile(b'gnamb 0000 00 (?:NC|CS|CM|CE) ([1-8]),"(.+?)" \r'), self.__MatchPresetBankName, None)
            self.AddMatchString(compile(b'[a-z]{5} NAK (01|02|03|04|05|90|92|93|99) ?\r'), self.__MatchError, None)
            
        self.AuxCmdString = None
        self.AudioOutput1CmdString = None
        self.InterpretationReturnCmdString = None
        self.MicLineCmdString = None

    def Setsxinp(self, value, qualifier):

        MicLineTypeStates = {
            '0dbV':   '0',
            '-10dbV': '1',
            '-20dbV': '2',
        }

        def replace(value, index):

            res = self.AuxCmdString
            x = -1
            for i in range(0, index):
                x = res.find(',', x + 1)
            y = res.find(',', x + 1)
            self.AuxCmdString = res[:x + 1] + str(value) + res[y:]

        if not self.AuxCmdString:
            self.Error(['Aux Input not received'])
        else:
            CmdString = 'sxinp S 0000 00 NC {} \r'.format(self.AuxCmdString)
            self.__SetHelper('AuxLevel', CmdString, value, qualifier)

    def __MatchAuxLevel(self, match, tag):

        States = {
            '0': '0dbV',
            '1': '-10dbV',
            '2': '-20dbV'
        }

        self.AuxCmdString = match.group(1).decode()
        res = match.group(1).decode().split(',')

        self.WriteStatus('AuxLevel',  int(res[0]) , None)
        self.WriteStatus('AuxNominalLevel', States[res[1]], None)

    def SetAuxLevel(self, value, qualifier):

        if 0 <= value <= 511:
            self.Setsxinp(value,qualifier)
        else:
            self.Discard('Invalid Command for SetAuxLevel')

    def UpdateAuxLevel(self, value, qualifier):

        self.__UpdateHelper('AuxLevel', 'gxinp O 0000 00 NC \r' , value, qualifier)

    def SetAuxNominalLevel(self, value, qualifier):

        ValueStateValues = ('0dbV', '-10dbV', '-20dbV')

        if value in ValueStateValues:
            self.Setsxinp(value,qualifier)
        else:
            self.Discard('Invalid Command for SetAuxNominalLevel')

    def UpdateAuxNominalLevel(self, value, qualifier):
            
        self.__UpdateHelper('AuxNominalLevel', 'gxinp O 0000 00 NC \r' , value, qualifier)

    def SetDelegateTalkControlCommand(self, value, qualifier):

        DUConstraints = {
            'Min': 0,
            'Max': 99999999,
        }
        UnitTypeStates = {
            'ATUC-50DU':  '0',
            'ATUC-50INT': '1',
            'ATUC-50IU':  '2',
            'ATUC-IRDU':  '3',
            'ATUC-50DUa': '4',
        }

        ValueStateValues = ('On', 'Off')

        du_number = qualifier['DU']
        unit_type = qualifier['Unit Type']
        if DUConstraints['Min'] <= du_number <= DUConstraints['Max'] and unit_type in UnitTypeStates and value in ValueStateValues:

            if value == 'On':
                if self.ReadStatus('DelegateTalkControlStatus', {'DU': du_number}) == 'Wait':
                    State = 'prmit'
                else:
                    State = 'reqon'
            else:
                if self.ReadStatus('DelegateTalkControlStatus', {'DU': du_number}) == 'Wait':
                    State = 'reqof'
                else:
                    State = 'takof'
            CmdString = '{} S 0000 00 NC 1,{},{}, \r'.format(State, du_number, UnitTypeStates[unit_type])
            self.__SetHelper('DelegateTalkControlCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelegateTalkControlCommand')

    def UpdateDelegateTalkControlStatus(self, value, qualifier):

        self.__UpdateHelper('DelegateTalkControlStatus', 'gtalk O 0000 00 NC  \r', value, qualifier)

    def __MatchDelegateTalkControlStatus(self, match, tag):

        ValueStateValues = {
            '1,0': 'On',
            '0,0': 'Off',
            '0,1': 'Wait',
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DelegateTalkControlStatus', value, {'DU': int(match.group(1).decode())})
        
    def UpdateFirmware(self, value, qualifier):

        self.__UpdateHelper('Firmware', 'gvers O 0000 00 NC \r' , value, qualifier)

    def __MatchFirmware(self, match, tag):

        self.WriteStatus('Firmware',  match.group(1).decode('iso-8859-1') , None)

    def Setsiinp(self, value, qualifier):

        States = {
            '0dbV'  : '0', 
            '+4dbV' : '1'
        }

        def replace(value,index):

            res = self.InterpretationReturnCmdString
            x = -1
            for i in range(0,index):
                x = res.find(',',x+1)
            y = res.find(',',x+1)
            self.InterpretationReturnCmdString = res[:x+1] + str(value) + res[y:]

        if self.InterpretationReturnCmdString == None:
            self.Error(['Interpretation Return not received'])
        else:
            CmdString = 'siinp S 0000 00 NC {} \r'.format(self.InterpretationReturnCmdString)
            self.__SetHelper('InterpretationReturnLevel', CmdString, value, qualifier)

    def __MatchInterpretationReturn(self, match, tag):

        States = {
            '0' : '0dbV', 
            '1' : '+4dbV'
        }

        self.InterpretationReturnCmdString = match.group(1).decode()
        res = match.group(1).decode().split(',')

        self.WriteStatus('InterpretationReturnLevel',  int(res[0]) , {'Input':'1'} )
        self.WriteStatus('InterpretationReturnNominalLevel',  States[res[1]] , {'Input':'1'} )
        self.WriteStatus('InterpretationReturnLevel',  int(res[15]) , {'Input':'2'} )
        self.WriteStatus('InterpretationReturnNominalLevel',  States[res[16]] , {'Input':'2'} )

    def SetInterpretationReturnLevel(self, value, qualifier):

        if 0 <= value <= 511 and 1 <= int(qualifier['Input']) <= 2:
            self.Setsiinp(value,qualifier)
        else:
            self.Discard('Invalid Command for SetInterpretationReturnLevel')

    def UpdateInterpretationReturnLevel(self, value, qualifier):

        self.__UpdateHelper('InterpretationReturnLevel', 'giinp O 0000 00 NC \r' , value, qualifier)

    def SetInterpretationReturnNominalLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 2:
            self.Setsiinp(value,qualifier)
        else:
            self.Discard('Invalid Command for SetInterpretationReturnNominalLevel')

    def UpdateInterpretationReturnNominalLevel(self, value, qualifier):

        self.__UpdateHelper('InterpretationReturnLevel', 'giinp O 0000 00 NC \r' , value, qualifier)

    def Setsminp(self, value, qualifier):

        MicLineTypeStates = {
            'Mic'           : '0', 
            'Line +4dBu'    : '1', 
            'Line'          : '2'
        }

        def replace(value,index):

            res = self.MicLineCmdString
            x = -1
            for i in range(0,index):
                x = res.find(',',x+1)
            y = res.find(',',x+1)
            self.MicLineCmdString = res[:x+1] + str(value) + res[y:]

        if self.MicLineCmdString == None:
            self.Error(['Input Setting not received'])
        else:
            CmdString = 'sminp S 0000 00 NC {} \r'.format(self.MicLineCmdString)
            self.__SetHelper('OutputLevel', CmdString, value, qualifier)

    def __MatchMicLine(self, match, tag):
    
        MicLineTypeStates = {
            '0' : 'Mic', 
            '1' : 'Line +4dBu', 
            '2' : 'Line'
        }

        self.MicLineCmdString = match.group(1).decode()

        res = match.group(1).decode().split(',')

        Type1 = MicLineTypeStates[res[0]]
        self.WriteStatus('MicLineType',  Type1 , {'Input':'1'} )

        Type2 = MicLineTypeStates[res[35]]
        self.WriteStatus('MicLineType',  Type2 , {'Input':'2'} )

        if Type1 == 'Mic':
            self.WriteStatus('MicLineGain',  int(res[4]) , {'Input':'1'} )
            self.WriteStatus('MicLineLevel',  int(res[5]) , {'Input':'1'} )
        else:
            self.WriteStatus('MicLineGain',  int(res[19]) , {'Input':'1'} )
            self.WriteStatus('MicLineLevel',  int(res[20]) , {'Input':'1'} )

        if Type2 == 'Mic':
            self.WriteStatus('MicLineGain',  int(res[39]) , {'Input':'2'} )
            self.WriteStatus('MicLineLevel',  int(res[40]) , {'Input':'2'} )
        else:
            self.WriteStatus('MicLineGain',  int(res[55]) , {'Input':'2'} )
            self.WriteStatus('MicLineLevel',  int(res[56]) , {'Input':'2'} )

    def SetMicLineGain(self, value, qualifier):

        if 0 <= value <= 44 and 1 <= int(qualifier['Input']) <= 2:
            self.Setsminp(value,qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineGain')

    def UpdateMicLineGain(self, value, qualifier):

        self.__UpdateHelper('MicLineGain', 'gminp O 0000 00 NC \r' , value, qualifier)

    def SetMicLineLevel(self, value, qualifier):

        if 0 <= value <= 511 and 1 <= int(qualifier['Input']) <= 2:
            self.Setsminp(value,qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineLevel')

    def UpdateMicLineLevel(self, value, qualifier):

        self.__UpdateHelper('MicLineLevel', 'gminp O 0000 00 NC \r' , value, qualifier)

    def SetMicLineType(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 2:
            self.Setsminp(value,qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineType')

    def UpdateMicLineType(self, value, qualifier):

        self.__UpdateHelper('MicLineType', 'gminp O 0000 00 NC \r' , value, qualifier)

    def Setsaout(self, value, qualifier):

        SourceStates = {
            'Floor'             : '0', 
            'Group 0'           : '1', 
            'Group 1'           : '2', 
            'Group 2'           : '3', 
            'Group 3'           : '4', 
            'Language 1'        : '5', 
            'Language 2'        : '6', 
            'Language 3'        : '7', 
            'Remote Language 1' : '8', 
            'Remote Language 2' : '9', 
            'Mic/ Line 1'       : '10', 
            'Mic/ Line 2'       : '11', 
            'Mic/ Line 1&2 Mix' : '12'
        }

        Output = qualifier['Output']
        Level = self.ReadStatus('OutputLevel', qualifier)
        src = self.ReadStatus('OutputSource', qualifier)
        if src:
            Source = SourceStates[src]

        if not self.AudioOutput1CmdString:
            self.Error(['Output Setting not received'])
        else:
            if Output == '1':
                CmdString = 'saout S 0000 00 NC {},{},{}'.format(Output, Level, Source) + self.AudioOutput1CmdString
            else:
                CmdString = 'saout S 0000 00 NC {},{},{} \r'.format(Output, Level, Source)
            self.__SetHelper('OutputLevel', CmdString, value, qualifier)

    def __MatchOutput(self, match, tag):

        Output = tag

        if Output == '1':
            self.AudioOutput1CmdString = match.group('String').decode()

        SourceStates = {
            '0' : 'Floor', 
            '1' : 'Group 0', 
            '2' : 'Group 1', 
            '3' : 'Group 2', 
            '4' : 'Group 3', 
            '5' : 'Language 1', 
            '6' : 'Language 2', 
            '7' : 'Language 3', 
            '8' : 'Remote Language 1', 
            '9' : 'Remote Language 2', 
            '10' : 'Mic/ Line 1', 
            '11' : 'Mic/ Line 2', 
            '12' : 'Mic/ Line 1&2 Mix'
        }


        qualifier = { 'Output' : Output }
        self.WriteStatus('OutputLevel',  int(match.group('Level').decode()) ,qualifier)
        self.WriteStatus('OutputSource',  SourceStates[match.group('Source').decode()] , qualifier)

    def SetOutputLevel(self, value, qualifier):

        if 0 <= value <= 511 and 1 <= int(qualifier['Output']) <= 4:
            self.Setsaout(value,qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        self.__UpdateHelper('OutputLevel', 'gaout O 0000 00 NC \r' , value, qualifier)

    def SetOutputSource(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 4:
            self.Setsaout(value,qualifier)
        else:
            self.Discard('Invalid Command for SetOutputSource')

    def UpdateOutputSource(self, value, qualifier):

        self.__UpdateHelper('OutputSource', 'gaout O 0000 00 NC \r' , value, qualifier)

    def UpdatePresetBankName(self, value, qualifier):

        PresetBankNameCmdString = 'gnamb O 0000 00 NC \r'
        self.__UpdateHelper('PresetBankName', PresetBankNameCmdString, value, qualifier)

    def __MatchPresetBankName(self, match, tag):

        qualifier = {'Number': match.group(1).decode()}
        value = match.group(2).decode().replace('""', '"')
        self.WriteStatus('PresetBankName', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 8:
            CmdString = 'callp S 0000 00 NC {} \r'.format(value) 
            self.__SetHelper('PresetRecall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 8:
            CmdString = 'savep S 0000 00 NC {} \r'.format(value) 
            self.__SetHelper('PresetSave', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetReboot(self, value, qualifier):

        self.__SetHelper('Reboot', 'rboot S 0000 00 NC \r' , value, qualifier)

    def UpdateRecordingElapsedTime(self, value, qualifier):

        self.UpdateSoundRecording( None, qualifier)

    def UpdateRecordingRemainingTime(self, value, qualifier):

        self.UpdateSoundRecording( None, qualifier)

    def SetSoundRecording(self, value, qualifier):

        States = {
            'Start' : '2', 
            'Stop'  : '0', 
            'Pause' : '1'
        }

        self.__SetHelper('SoundRecording', 'recmd S 0000 00 NC {} \r'.format(States[value]) , value, qualifier)

    def UpdateSoundRecording(self, value, qualifier):
            
        self.__UpdateHelper('SoundRecording','recst O 0000 00 NC \r' , value, qualifier)

    def __MatchSoundRecording(self, match, tag):

        States = {
            '2': 'Start',
            '0': 'Stop',
            '1': 'Pause'
        }

        self.WriteStatus('SoundRecording', States[match.group(1).decode()], None)

        rec_time_value = match.group(2).decode()
        value = ':'.join(rec_time_value[i:i + 2] for i in range(0, 6, 2))
        self.WriteStatus('RecordingElapsedTime', value, None)

        rem_time_value = match.group(3).decode()
        value = ':'.join(rem_time_value[i:i + 2] for i in range(0, 6, 2))
        self.WriteStatus('RecordingRemainingTime', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        ErrorCodes = {
            '01' : 'Grammar error.',
            '02' : 'Invalid command.',
            '03' : 'Divided Transmission Error.',
            '04' : 'Parameter error.',
            '05' : 'Transmit timeout.',
            '90' : 'Busy.',
            '92' : 'Busy (Safe Mode).',
            '93' : 'Busy (Extension).',
            '99' : 'Other errors.'
            }

        self.Error([ErrorCodes[match.group(1).decode()]])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.AuxCmdString = None
        self.AudioOutput1CmdString = None
        self.InterpretationReturnCmdString = None
        self.MicLineCmdString = None

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()