from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
            'GroupEnableDisable': {'Parameters':['Group'], 'Status': {}},
            'LineEnableDisable': {'Parameters':['Group/Zone','Input'], 'Status': {}},
            'LineInputGain': {'Parameters':['Input'], 'Status': {}},
            'MicrophoneEnableDisable': {'Parameters':['Group/Zone','Microphone'], 'Status': {}},
            'MusicLevel': {'Parameters':['Group/Zone'], 'Status': {}},
            'Mute': {'Parameters':['Group/Zone'], 'Status': {}},
            'Source': {'Parameters':['Group/Zone'], 'Status': {}},
            'Version': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'<g([1-4]),q=[1-8,]*(e|d)/>'), self.__MatchGroupEnableDisable, None)
            self.AddMatchString(re.compile(b'<(g[1-4]|z[1-8]).l([1-8]),q=(e|d), pri = (on|off)/>'), self.__MatchLineEnableDisable, None)
            self.AddMatchString(re.compile(b'<l([1-8]),g=(0|[+\-]1?[0-9])/>'), self.__MatchLineInputGain, None)
            self.AddMatchString(re.compile(b'<(g[1-4]|z[1-8]).m([1-4]),q=(e|d), pri = (on|off)/>'), self.__MatchMicrophoneEnableDisable, None)
            self.AddMatchString(re.compile(b'<(g[1-4]|z[1-8]).mu,(mute|l=([0-9]{1,2}))/>'), self.__MatchMusicLevel, None)
            self.AddMatchString(re.compile(b'<(g[1-4]|z[1-8]).mu,s=([1-8])/>'), self.__MatchSource, None)
            self.AddMatchString(re.compile(b'<sy,vq sw=([0-9.]+) hw=[0-9.]+/>'), self.__MatchVersion, None)
            self.AddMatchString(re.compile(b'<!(I|B|T|P|E|A)[\s\S]*/>$'), self.__MatchError, None)

    def SetGroupEnableDisable(self, value, qualifier):

        GroupStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        ValueStateValues = {
            'Enable' : 'E', 
            'Disable' : 'D'
        }

        GroupEnableDisableCmdString = '<G{0},{1}/>'.format(GroupStates[qualifier['Group']], ValueStateValues[value])
        self.__SetHelper('GroupEnableDisable', GroupEnableDisableCmdString, value, qualifier)

    def UpdateGroupEnableDisable(self, value, qualifier):

        GroupStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        GroupEnableDisableCmdString = '<G{0},Q/>'.format(GroupStates[qualifier['Group']])
        self.__UpdateHelper('GroupEnableDisable', GroupEnableDisableCmdString, value, qualifier)

    def __MatchGroupEnableDisable(self, match, tag):

        GroupStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        ValueStateValues = {
            'e' : 'Enable', 
            'd' : 'Disable'
        }

        qualifier = {}
        qualifier['Group'] = GroupStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('GroupEnableDisable', value, qualifier)

    def SetLineEnableDisable(self, value, qualifier):

        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        InputStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        ValueStateValues = {
            'Enable' : 'E', 
            'Disable' : 'D'
        }

        LineEnableDisableCmdString = '<{0}.L{1},{2}/>'.format(GroupZoneStates[qualifier['Group/Zone']], InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('LineEnableDisable', LineEnableDisableCmdString, value, qualifier)

    def UpdateLineEnableDisable(self, value, qualifier):


        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        InputStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        LineEnableDisableCmdString = '<{0}.L{1},Q/>'.format(GroupZoneStates[qualifier['Group/Zone']], InputStates[qualifier['Input']])
        self.__UpdateHelper('LineEnableDisable', LineEnableDisableCmdString, value, qualifier)

    def __MatchLineEnableDisable(self, match, tag):

        GroupZoneStates = {
            'g1' : 'Group 1', 
            'g2' : 'Group 2', 
            'g3' : 'Group 3', 
            'g4' : 'Group 4', 
            'z1' : 'Zone 1', 
            'z2' : 'Zone 2', 
            'z3' : 'Zone 3', 
            'z4' : 'Zone 4', 
            'z5' : 'Zone 5', 
            'z6' : 'Zone 6', 
            'z7' : 'Zone 7', 
            'z8' : 'Zone 8'
        }

        InputStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        ValueStateValues = {
            'e' : 'Enable', 
            'd' : 'Disable'
        }

        qualifier = {}
        qualifier['Group/Zone'] = GroupZoneStates[match.group(1).decode()]
        qualifier['Input'] = InputStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('LineEnableDisable', value, qualifier)

    def SetLineInputGain(self, value, qualifier):

        InputStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        ValueConstraints = {
            'Min' : -12,
            'Max' : 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value == 0:
                LineInputGainCmdString = '<L{0},G0/>'.format(InputStates[qualifier['Input']])
            else:
                LineInputGainCmdString = '<L{0},G{1:+}/>'.format(InputStates[qualifier['Input']], value)
            self.__SetHelper('LineInputGain', LineInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        
        InputStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        LineInputGainCmdString = '<L{0},GQ/>'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('LineInputGain', LineInputGainCmdString, value, qualifier)

    def __MatchLineInputGain(self, match, tag):

        InputStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('LineInputGain', value, qualifier)

    def SetMicrophoneEnableDisable(self, value, qualifier):

        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        MicrophoneStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        ValueStateValues = {
            'Enable' : 'E', 
            'Disable' : 'D'
        }

        MicrophoneEnableDisableCmdString = '<{0}.M{1},{2}/>'.format(GroupZoneStates[qualifier['Group/Zone']], MicrophoneStates[qualifier['Microphone']], ValueStateValues[value])
        self.__SetHelper('MicrophoneEnableDisable', MicrophoneEnableDisableCmdString, value, qualifier)

    def UpdateMicrophoneEnableDisable(self, value, qualifier):


        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        MicrophoneStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        MicrophoneEnableDisableCmdString = '<{0}.M{1},Q/>'.format(GroupZoneStates[qualifier['Group/Zone']], MicrophoneStates[qualifier['Microphone']])
        self.__UpdateHelper('MicrophoneEnableDisable', MicrophoneEnableDisableCmdString, value, qualifier)

    def __MatchMicrophoneEnableDisable(self, match, tag):

        GroupZoneStates = {
            'g1' : 'Group 1', 
            'g2' : 'Group 2', 
            'g3' : 'Group 3', 
            'g4' : 'Group 4', 
            'z1' : 'Zone 1', 
            'z2' : 'Zone 2', 
            'z3' : 'Zone 3', 
            'z4' : 'Zone 4', 
            'z5' : 'Zone 5', 
            'z6' : 'Zone 6', 
            'z7' : 'Zone 7', 
            'z8' : 'Zone 8'
        }

        MicrophoneStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        ValueStateValues = {
            'e' : 'Enable', 
            'd' : 'Disable'
        }

        qualifier = {}
        qualifier['Group/Zone'] = GroupZoneStates[match.group(1).decode()]
        qualifier['Microphone'] = MicrophoneStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MicrophoneEnableDisable', value, qualifier)

    def SetMusicLevel(self, value, qualifier):

        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        ValueConstraints = {
            'Min' : -62,
            'Max' : 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MusicLevelCmdString = '<{0}.MU,L{1}/>'.format(GroupZoneStates[qualifier['Group/Zone']], abs(value))
            self.__SetHelper('MusicLevel', MusicLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMusicLevel')

    def UpdateMusicLevel(self, value, qualifier):


        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        MusicLevelCmdString = '<{0}.MU,LQ/>'.format(GroupZoneStates[qualifier['Group/Zone']])
        self.__UpdateHelper('MusicLevel', MusicLevelCmdString, value, qualifier)

    def __MatchMusicLevel(self, match, tag):

        GroupZoneStates = {
            'g1' : 'Group 1', 
            'g2' : 'Group 2', 
            'g3' : 'Group 3', 
            'g4' : 'Group 4', 
            'z1' : 'Zone 1', 
            'z2' : 'Zone 2', 
            'z3' : 'Zone 3', 
            'z4' : 'Zone 4', 
            'z5' : 'Zone 5', 
            'z6' : 'Zone 6', 
            'z7' : 'Zone 7', 
            'z8' : 'Zone 8'
        }

        qualifier = {}
        qualifier['Group/Zone'] = GroupZoneStates[match.group(1).decode()]

        match2 = match.group(2).decode()
        if match2 == 'mute':
            value = -62
        else:
            value = -int(match.group(3).decode())
        self.WriteStatus('MusicLevel', value, qualifier)

    def SetMute(self, value, qualifier):

        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        MuteCmdString = '<{0}.MU,M/>'.format(GroupZoneStates[qualifier['Group/Zone']])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)
    def SetSource(self, value, qualifier):

        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        SourceCmdString = '<{0}.MU,S{1}/>'.format(GroupZoneStates[qualifier['Group/Zone']], ValueStateValues[value])
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):


        GroupZoneStates = {
            'Group 1' : 'G1', 
            'Group 2' : 'G2', 
            'Group 3' : 'G3', 
            'Group 4' : 'G4', 
            'Zone 1' : 'Z1', 
            'Zone 2' : 'Z2', 
            'Zone 3' : 'Z3', 
            'Zone 4' : 'Z4', 
            'Zone 5' : 'Z5', 
            'Zone 6' : 'Z6', 
            'Zone 7' : 'Z7', 
            'Zone 8' : 'Z8'
        }

        SourceCmdString = '<{0}.MU,SQ/>'.format(GroupZoneStates[qualifier['Group/Zone']])
        self.__UpdateHelper('Source', SourceCmdString, value, qualifier)

    def __MatchSource(self, match, tag):

        GroupZoneStates = {
            'g1' : 'Group 1', 
            'g2' : 'Group 2', 
            'g3' : 'Group 3', 
            'g4' : 'Group 4', 
            'z1' : 'Zone 1', 
            'z2' : 'Zone 2', 
            'z3' : 'Zone 3', 
            'z4' : 'Zone 4', 
            'z5' : 'Zone 5', 
            'z6' : 'Zone 6', 
            'z7' : 'Zone 7', 
            'z8' : 'Zone 8'
        }

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8'
        }

        qualifier = {}
        qualifier['Group/Zone'] = GroupZoneStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Source', value, qualifier)

    def UpdateVersion(self, value, qualifier):

        VersionCmdString = '<SY,VQ/>'
        self.__UpdateHelper('Version', VersionCmdString, value, qualifier)

    def __MatchVersion(self, match, tag):

        self.WriteStatus('Version', match.group(1).decode(), None)

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
            'I' : 'Interrupted',
            'B' : 'Buffer Overflow',
            'T' : 'Tokenise Error',
            'P' : 'Parse Error',
            'E' : 'Execution Error',
            'A' : 'Overrun Error'
        }

        self.Error(['Error: {0}'.format(ErrorCodes[match.group(1).decode()])])

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()