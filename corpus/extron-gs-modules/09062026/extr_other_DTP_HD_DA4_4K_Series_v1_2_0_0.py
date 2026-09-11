from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, match, search
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
            'DTP HD DA4 4K 230': self.extr_31_1180_4,
            'DTP HD DA4 4K 330': self.extr_31_1180_4,
            'DTP HD DA8 4K 230': self.extr_31_1180_8,
            'DTP HD DA8 4K 330': self.extr_31_1180_8,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalHDCPMode': {'Status': {}},
            'GlobalHDMIAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPAuthorization': {'Status': {}},
            'HDCPMode': {'Parameters': ['Output'], 'Status': {}},
            'HDMIAudioMute': {'Parameters': ['Output'], 'Status': {}},
            'InputHDCPStatus': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Type'], 'Status': {}},
            'OutputHDCPStatus': {'Parameters': ['Output'], 'Status': {}},
            'OutputSignalStatus': {'Parameters': ['Output'], 'Status': {}},
            'PartNumber': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

        self.lastAudioMuteUpdate = 0
        self.lastHDCPModeUpdate = 0
        self.lastHDCPStatusUpdate = 0
        self.lastHDMIAudioMuteUpdate = 0
        self.lastSignalStatusUpdate = 0
        self.lastVideoMuteUpdate = 0

        self.EchoDisabled = True
        self.VerboseDisabled = True
       
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Amt[0-1] (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Amt[0-1] (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Amt(0|1)\r\n'), self.__MatchGlobalAudioMute, None)
            self.AddMatchString(compile(rb'Amt(1|2|3|4|5|6|7|8)\*(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'HdcpE(0|1)\r\n'), self.__MatchHDCPAuthorization, None)
            self.AddMatchString(compile(b'HdcpS[0-3] (0|1|2|3) (0|1|2|3) (0|1|2|3) (0|1|2|3)\r\n'), self.__MatchHDCPMode, None)
            self.AddMatchString(compile(b'HdcpS[0-3] (0|1|2|3) (0|1|2|3) (0|1|2|3) (0|1|2|3) (0|1|2|3) (0|1|2|3) (0|1|2|3) (0|1|2|3)\r\n'), self.__MatchHDCPMode, None)
            self.AddMatchString(compile(b'HdcpS(0|1|2|3)\r\n'), self.__MatchGlobalHDCPMode, None)
            self.AddMatchString(compile(rb'HdcpS0?(1|2|3|4|5|6|7|8)\*(0|1|2|3)\r\n'), self.__MatchHDCPMode, None)
            self.AddMatchString(compile(b'Afmt[0-1] (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchHDMIAudioMute, None)
            self.AddMatchString(compile(b'Afmt[0-1] (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchHDMIAudioMute, None)
            self.AddMatchString(compile(b'Afmt(0|1)\r\n'), self.__MatchGlobalHDMIAudioMute, None)
            self.AddMatchString(compile(rb'Afmt(1|2|3|4|5|6|7|8)\*(0|1)\r\n'), self.__MatchHDMIAudioMute, None)
            self.AddMatchString(compile(rb'Hdcp(0|1)\*(0|1) (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchOutputHDCPStatus, None)
            self.AddMatchString(compile(rb'Hdcp(0|1)\*(0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchOutputHDCPStatus, None)
            self.AddMatchString(compile(rb'Sig(0|1)\*(0|1) (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchOutputSignalStatus, None)
            self.AddMatchString(compile(rb'Sig(0|1)\*(0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1) (0|1)\r\n'), self.__MatchOutputSignalStatus, None)
            self.AddMatchString(compile(b'Vmt[0-2] (0|1|2) (0|1|2) (0|1|2) (0|1|2)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Vmt(0|1|2)\r\n'), self.__MatchGlobalVideoMute, None)
            self.AddMatchString(compile(b'Vmt[0-2] (0|1|2) (0|1|2) (0|1|2) (0|1|2) (0|1|2) (0|1|2) (0|1|2) (0|1|2)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(rb'Vmt(1|2|3|4|5|6|7|8)\*(0|1|2)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'E(01|10|13|24|28)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Echo0\r\n'), self.__MatchEchoMode, None)
            self.AddMatchString(compile(rb'Pno(\d{2}-\d{4}-\d{2})\r\n'), self.__MatchPartNumber, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        output = qualifier['Output']

        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            AudioMuteCmdString = '{0}*{1}Z'.format(output, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        output = qualifier['Output']
        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        if len(match.group(0).decode()) == 8:
            self.WriteStatus('AudioMute', ValueStateValues[match.group(2).decode()], {'Output': '{}'.format(match.group(1).decode())})
        elif len(match.group(0).decode()) == 6:
            for i in range(1, self.OutputSize + 1):
                self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output': '{}'.format(i)})
        else:
            for i in range(1, self.OutputSize + 1):
                self.WriteStatus('AudioMute', ValueStateValues[match.group(i).decode()], {'Output': '{}'.format(i)})

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            GlobalAudioMuteCmdString = '{0}Z\r'.format(ValueStateValues[value])
            self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def __MatchGlobalAudioMute(self, match, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        for i in range(1, self.OutputSize + 1):
            self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output': '{}'.format(i)})

    def SetGlobalHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'Follow Input': '0',
            'Always Encrypt Output': '1',
            'Follow Input (With cont DVI trials)': '2',
            'Always Encrypt Output (With cont DVI trials)': '3'
        }

        if value in ValueStateValues:
            GlobalHDCPModeCmdString = 'WS{0}HDCP\r'.format(ValueStateValues[value])
            self.__SetHelper('GlobalHDCPMode', GlobalHDCPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalHDCPMode')

    def __MatchGlobalHDCPMode(self, match, qualifier):

        ValueStateValues = {
            '0': 'Follow Input',
            '1': 'Always Encrypt Output',
            '2': 'Follow Input (With cont DVI trials)',
            '3': 'Always Encrypt Output (With cont DVI trials)'
        }

        for i in range(1, self.OutputSize + 1):
            self.WriteStatus('HDCPMode', ValueStateValues[match.group(1).decode()], {'Output': '{}'.format(i)})
            
    def SetGlobalHDMIAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            GlobalHDMIAudioMuteCmdString = 'W{0}AFMT\r'.format(ValueStateValues[value])
            self.__SetHelper('GlobalHDMIAudioMute', GlobalHDMIAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalHDMIAudioMute')

    def __MatchGlobalHDMIAudioMute(self, match, qualifier):


        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        for i in range(1, self.OutputSize+1):
            self.WriteStatus('HDMIAudioMute', ValueStateValues[match.group(1).decode()], {'Output': '{}'.format(i)})
            
    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0',
            'Sync': '2'
        }

        if value in ValueStateValues:
            GlobalVideoMuteCmdString = '{0}B\r'.format(ValueStateValues[value])
            self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def __MatchGlobalVideoMute(self, match, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Sync'
        }

        for i in range(1, self.OutputSize+1):
            self.WriteStatus('VideoMute', ValueStateValues[match.group(1).decode()], {'Output' : '{}'.format(i)})
            
    def SetHDCPAuthorization(self, value, qualifier):


        ValueStateValues = {
            'Enable' : '1',
            'Disable': '0'
        }

        if value in ValueStateValues:
            HDCPAuthorizationCmdString = 'WE{0}HDCP\r'.format(ValueStateValues[value])
            self.__SetHelper('HDCPAuthorization', HDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPAuthorization')

    def UpdateHDCPAuthorization(self, value, qualifier):

        HDCPAuthorizationCmdString = 'WEHDCP\r'
        self.__UpdateHelper('HDCPAuthorization', HDCPAuthorizationCmdString, value, qualifier)

    def __MatchHDCPAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPAuthorization', value, None)

    def SetHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'Follow Input'                                : '0', 
            'Always Encrypt Output'                       : '1', 
            'Follow Input (With cont DVI trials)'          : '2', 
            'Always Encrypt Output (With cont DVI trials)' : '3'
        }

        output = qualifier['Output']

        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            self.__SetHelper('HDCPMode', 'WS{0}*{1}HDCP\r'.format(output, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPMode')

    def UpdateHDCPMode(self, value, qualifier):


        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:           
            HDCPModeCmdString = 'WSHDCP\r'
            self.__UpdateHelper('HDCPMode', HDCPModeCmdString, value, qualifier)          
        else:
            self.Discard('Device Is Busy for UpdateHDCPMode')

    def __MatchHDCPMode(self, match, tag):

        ValueStateValues = {
            '0': 'Follow Input',
            '1': 'Always Encrypt Output',
            '2': 'Follow Input (With cont DVI trials)',
            '3': 'Always Encrypt Output (With cont DVI trials)'
        }

        if len(match.group(0).decode()) == 10 or len(match.group(0).decode()) == 11:
            self.WriteStatus('HDCPMode', ValueStateValues[match.group(2).decode()], {'Output' : '{}'.format(match.group(1).decode())})
        elif len(match.group(0).decode()) == 8:
            for i in range(1, self.OutputSize+1):
                self.WriteStatus('HDCPMode', ValueStateValues[match.group(1).decode()], {'Output' : '{}'.format(i)})
        else:
            for i in range(1, self.OutputSize+1):
                self.WriteStatus('HDCPMode', ValueStateValues[match.group(i).decode()], {'Output' : '{}'.format(i)})

    def SetHDMIAudioMute(self, value, qualifier):


        ValueStateValues = {
            'Off': '0',
            'On' : '1'
        }

        output = qualifier['Output']

        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            self.__SetHelper('HDMIAudioMute', 'W{0}*{1}AFMT\r'.format(output, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIAudioMute')

    def UpdateHDMIAudioMute(self, value, qualifier):


        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            HDMIAudioMuteCmdString = 'WAFMT\r'
            self.__UpdateHelper('HDMIAudioMute', HDMIAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateHDMIAudioMute')

    def __MatchHDMIAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        if len(match.group(0).decode()) == 9:
            self.WriteStatus('HDMIAudioMute', ValueStateValues[match.group(2).decode()], {'Output' : '{}'.format(match.group(1).decode())})
        elif len(match.group(0).decode()) == 7:
            for i in range(1, self.OutputSize+1):
                self.WriteStatus('HDMIAudioMute', ValueStateValues[match.group(1).decode()], {'Output' : '{}'.format(i)})
        else:
            for i in range(1, self.OutputSize+1):
                self.WriteStatus('HDMIAudioMute', ValueStateValues[match.group(i).decode()], {'Output' : '{}'.format(i)})
            
    def UpdateInputHDCPStatus(self, value, qualifier):

        if qualifier['Type'] in ['Loop Through', 'HDMI']:
            self.UpdateOutputHDCPStatus(None, {'Output': '1'})
        else:
            self.Discard('Invalid Command for UpdateInputHDCPStatus')

    def UpdateInputSignalStatus(self, value, qualifier):

        if qualifier['Type'] in ['Loop Through', 'HDMI']:
            self.UpdateOutputSignalStatus(None, {'Output': '1'})
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def UpdateOutputHDCPStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputHDCPStatusCmdString = 'WHDCP\r'
            self.__UpdateHelper('OutputHDCPStatus', OutputHDCPStatusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateOutputHDCPStatus')

    def __MatchOutputHDCPStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Enabled',
            '0': 'Disabled'
        }

        self.WriteStatus('InputHDCPStatus', ValueStateValues[match.group(1).decode()], {'Type': 'HDMI'})
        self.WriteStatus('InputHDCPStatus', ValueStateValues[match.group(2).decode()], {'Type': 'Loop Through'})
        
        for i in range(1, self.OutputSize+1):
            self.WriteStatus('OutputHDCPStatus', ValueStateValues[match.group(i+2).decode()], {'Output': '{}'.format(i)})
        
    def UpdateOutputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputSignalStatusCmdString = 'WLS\r'
            self.__UpdateHelper('OutputSignalStatus', OutputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateOutputSignalStatus')

    def __MatchOutputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Enabled',
            '0': 'Disabled'
        }

        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(1).decode()], {'Type': 'HDMI'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(2).decode()], {'Type': 'Loop Through'})
        
        for i in range(1, self.OutputSize+1):
            self.WriteStatus('OutputSignalStatus', ValueStateValues[match.group(i+2).decode()], {'Output': '{}'.format(i)})
        
    def UpdatePartNumber(self, value, qualifier):        
        
        self.__UpdateHelper('PartNumber', 'N', value, qualifier)

    def __MatchPartNumber(self, match, tag):

        self.WriteStatus('PartNumber', match.group(1).decode(), None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Off' : '0',
            'On'  : '1',
            'Sync': '2'
        }

        output = qualifier['Output']

        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            VideoMuteCmdString = '{0}*{1}B'.format(output, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):
        
        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            VideoMuteCmdString = 'B'
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On',
            '2': 'Sync'
        }

        if len(match.group(0).decode()) == 8:
            self.WriteStatus('VideoMute', ValueStateValues[match.group(2).decode()], {'Output' : '{}'.format(match.group(1).decode())})
        elif len(match.group(0).decode()) == 6:
            for i in range(1, self.OutputSize+1):
                self.WriteStatus('VideoMute', ValueStateValues[match.group(1).decode()], {'Output' : '{}'.format(i)})
        else:
            for i in range(1, self.OutputSize+1):
                self.WriteStatus('VideoMute', ValueStateValues[match.group(i).decode()], {'Output' : '{}'.format(i)})
        
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

    def __MatchError(self, match, tag):
        self.counter = 0
        ErrorCodes = {
            '01': 'Invalid Output Channel Number',
            '10': 'Invalid Command',
            '13': 'Invalid Value',
            '24': 'Privilege violation',
            '28': 'Bad filename or file not found',
        }
        
        value = match.group(1).decode()
        if value in ErrorCodes:
            self.Error([ErrorCodes[value]])
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

    def extr_31_1180_4(self):   
        
        self.OutputSize = 4    
        
    def extr_31_1180_8(self):    
        
        self.OutputSize = 8

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
