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
        self.devicePassword = None

        self.Models = {
            'SS-R250N'   : self.tasc_31_3294_R,
            'SS-CDR250N' : self.tasc_31_3294_CDR
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentTrackInformation': { 'Status': {}},
            'CurrentTrackNumber': { 'Status': {}},
            'CurrentTrackTimeInformation': {'Parameters':['Type'], 'Status': {}},
            'DeviceSelect': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Eject': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'JOGPlayback': { 'Status': {}},
            'Pause': { 'Status': {}},
            'Playback': { 'Status': {}},
            'PlayMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'RecordMode': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'ShuffleMode': { 'Status': {}},
            'Skip': { 'Status': {}},
            'TrackName': {'Parameters':['Number'], 'Status': {}},
        }
        
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'0D7([0-9]{2})\r|0D7[0-9]{4}([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})\r'), self.__MatchCurrentTrackInformation, None)
            self.AddMatchString(re.compile(b'0D50[01]([0-9]{2})0([0-9])\r'), self.__MatchCurrentTrackNumber, None)
            self.AddMatchString(re.compile(b'0D80([0-3])([0-9]{2})([0-9]{2})([0-5][0-9]|60)([0-9]{2})\r'), self.__MatchCurrentTrackTimeInformation, None)
            self.AddMatchString(re.compile(b'0FF01(00|01|10|11)\r'), self.__MatchDeviceSelect, None)
            self.AddMatchString(re.compile(b'0D0(00|01|10|11|12|28|29|80|81|82|83|FF)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'0CC0([01])\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'0FF1290000(000|001|100|101|200)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'0CE0([01456])\r'), self.__MatchPlayMode, None)
            self.AddMatchString(re.compile(b'0B70([01])\r'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'0D9([0-9]{2})0([0-9])(.*?)\r'), self.__MatchTrackName, None)
            self.AddMatchString(re.compile(b'0F2\r'), self.__MatchError, None)

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'Enter Password'), self.__MatchPasswordPrompt, None)
            self.AddMatchString(re.compile(b'Login Successful'), self.__MatchLoginSuccess, None)

    def __MatchPasswordPrompt(self, match, tag):

        self.Authenticated = 'Not Authenticated'
        self.SetPassword( None, None)

    def SetPassword(self, value, qualifier):

        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLoginSuccess(self, match, tag):

        self.Authenticated = 'Authenticated'
        
    def makeCmndString(self, cmd_string):

        if 'Serial' in self.ConnectionType:
            final_cmndString = '\n0{}\r'.format(cmd_string)
        else:
            final_cmndString = '0{}\r\n'.format(cmd_string)
        return (final_cmndString)
    
    def UpdateCurrentTrackInformation(self, value, qualifier):

        CurrentTrackInformationCmdString = '57'
        self.__UpdateHelper('CurrentTrackInformation', self.makeCmndString(CurrentTrackInformationCmdString), value, qualifier)

    def __MatchCurrentTrackInformation(self, match, tag):

        if match.group(1):
            value = 'Program Number: ' + match.group(1).decode()
            self.WriteStatus('CurrentTrackInformation', value, None)
        else:
            value = ''.join([match.group(3).decode(), match.group(2).decode(), ':', match.group(4).decode(), ':', match.group(5).decode()])
            self.WriteStatus('CurrentTrackInformation', value, None)

    def UpdateCurrentTrackNumber(self, value, qualifier):

        CurrentTrackNumberCmdString = '55'
        self.__UpdateHelper('CurrentTrackNumber', self.makeCmndString(CurrentTrackNumberCmdString), value, qualifier)

    def __MatchCurrentTrackNumber(self, match, tag):

        numb_val = ''.join([match.group(2).decode(), match.group(1).decode()])
        value = int(numb_val)
        self.WriteStatus('CurrentTrackNumber', value, None)

    def UpdateCurrentTrackTimeInformation(self, value, qualifier):

        TypeStates = {
            'Elapsed Time'                      : '00', 
            'Track Remaining Time'              : '01', 
            'Total Elapsed Time on the Media'   : '02', 
            'Total Remaining Time on the Media' : '03'
        }
        
        type_val = qualifier['Type']
        if type_val in TypeStates:
            CurrentTrackTimeInformationCmdString = '58{0}'.format(TypeStates[type_val])
            self.__UpdateHelper('CurrentTrackTimeInformation', self.makeCmndString(CurrentTrackTimeInformationCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCurrentTrackTimeInformation')

    def __MatchCurrentTrackTimeInformation(self, match, tag):

        TypeStates = {
            '0' : 'Elapsed Time', 
            '1' : 'Track Remaining Time', 
            '2' : 'Total Elapsed Time on the Media', 
            '3' : 'Total Remaining Time on the Media'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = ''.join([match.group(3).decode(), match.group(2).decode(), ':', match.group(4).decode(), ':', match.group(5).decode()])
        self.WriteStatus('CurrentTrackTimeInformation', value, qualifier)

    def SetDeviceSelect(self, value, qualifier):

        if value in self.DeviceSelectStates:
            DeviceSelectCmdString = '7F01{}'.format(self.DeviceSelectStates[value])
            self.__SetHelper('DeviceSelect', self.makeCmndString(DeviceSelectCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceSelect')

    def UpdateDeviceSelect(self, value, qualifier):

        DeviceSelectCmdString = '7F01FF'
        self.__UpdateHelper('DeviceSelect', self.makeCmndString(DeviceSelectCmdString), value, qualifier)

    def __MatchDeviceSelect(self, match, tag):

        value = self.DeviceSelectValues[match.group(1).decode()]
        self.WriteStatus('DeviceSelect', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '50'
        self.__UpdateHelper('DeviceStatus', self.makeCmndString(DeviceStatusCmdString), value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00' : 'No Media',
            '01' : 'Preparing for disc ejection',
            '10' : 'Stop',
            '11' : 'Play',
            '12' : 'Ready',
            '28' : 'Cue',
            '29' : 'Review',
            '80' : 'Monitor',
            '81' : 'Record',
            '82' : 'Record Ready',
            '83' : 'Information Writing',
            'FF' : 'Other'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetEject(self, value, qualifier):

        EjectCmdString = '18'
        self.__SetHelper('Eject', self.makeCmndString(EjectCmdString), value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Only Remote'          : '0',
            'Remote and Front Key' : '1'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '4C0{}'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', self.makeCmndString(ExecutiveModeCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = '4CFF'
        self.__UpdateHelper('ExecutiveMode', self.makeCmndString(ExecutiveModeCmdString), value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Only Remote',
            '1' : 'Remote and Front Key'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Analog Balanced'   : '000',
            'Analog Unbalanced' : '001',
            'Digital XLR'       : '100',
            'Digital Coaxial'   : '101',
            'IF-DA2 (DANTE)'    : '200'
        }

        if value in ValueStateValues:
            InputCmdString = '7F1210000{}'.format(ValueStateValues[value])
            self.__SetHelper('Input', self.makeCmndString(InputCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '7F121000FF'
        self.__UpdateHelper('Input', self.makeCmndString(InputCmdString), value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '000' : 'Analog Balanced',
            '001' : 'Analog Unbalanced',
            '100' : 'Digital XLR',
            '101' : 'Digital Coaxial',
            '200' : 'IF-DA2 (DANTE)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetJOGPlayback(self, value, qualifier):

        ValueStateValues = {
            'On'      : '00',
            'Off'     : '01',
            'Forward' : '10',
            'Reverse' : '11'
        }

        if value in ValueStateValues:
            JOGPlaybackCmdString = '15{}'.format(ValueStateValues[value])
            self.__SetHelper('JOGPlayback', self.makeCmndString(JOGPlaybackCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetJOGPlayback')

    def SetPause(self, value, qualifier):

        PauseCmdString = '1401'
        self.__SetHelper('Pause', self.makeCmndString(PauseCmdString), value, qualifier)
        
    def SetPlayback(self, value, qualifier):

        ValueStateValues = {
            'Play' : '12',
            'Stop' : '10'
        }

        if value in ValueStateValues:
            PlaybackCmdString = ValueStateValues[value]
            self.__SetHelper('Playback', self.makeCmndString(PlaybackCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlayback')

    def SetPlayMode(self, value, qualifier):

        ValueStateValues = {
            'Continuous' : '0',
            'Single'     : '1',
            'Program'    : '4',
            'Random'     : '6'
        }

        if value in ValueStateValues:
            PlayModeCmdString = '4D0{}'.format(ValueStateValues[value])
            self.__SetHelper('PlayMode', self.makeCmndString(PlayModeCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlayMode')

    def UpdatePlayMode(self, value, qualifier):

        PlayModeCmdString = '4E'
        self.__UpdateHelper('PlayMode', self.makeCmndString(PlayModeCmdString), value, qualifier)

    def __MatchPlayMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Continuous',
            '1' : 'Single',
            '4' : 'Program',
            '5' : 'Program',
            '6' : 'Random'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PlayMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : '00',
            'Off'   : '11',
            'Reset' : '80'
        }

        if value in ValueStateValues:
            PowerCmdString = '75{}'.format(ValueStateValues[value])
            self.__SetHelper('Power', self.makeCmndString(PowerCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetRecordMode(self, value, qualifier):

        ValueStateValues = {
            'Record'        : '00',
            'Record Ready'  : '01',
            'Track Mark'    : '02',
            'Input Monitor' : '10'
        }

        if value in ValueStateValues:
            RecordModeCmdString = '13{}'.format(ValueStateValues[value])
            self.__SetHelper('RecordMode', self.makeCmndString(RecordModeCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordMode')

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            RepeatCmdString = '370{}'.format(ValueStateValues[value])
            self.__SetHelper('Repeat', self.makeCmndString(RepeatCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetRepeat')

    def UpdateRepeat(self, value, qualifier):

        RepeatCmdString = '37FF'
        self.__UpdateHelper('Repeat', self.makeCmndString(RepeatCmdString), value, qualifier)

    def __MatchRepeat(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Repeat', value, None)

    def SetShuffleMode(self, value, qualifier):

        ValueStateValues = {
            'Forward' : '0',
            'Reverse' : '1'
        }

        if value in ValueStateValues:
            ShuffleModeCmdString = '160{}'.format(ValueStateValues[value])
            self.__SetHelper('ShuffleMode', self.makeCmndString(ShuffleModeCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetShuffleMode')

    def SetSkip(self, value, qualifier):

        ValueStateValues = {
            'Track Skip Next'     : '00',
            'Track Skip Previous' : '01',
            'Mark Skip Next'      : '20',
            'Mark Skip Previous'  : '21',
            'Time Skip Next'      : '30',
            'Time Skip Previous'  : '31'
        }

        if value in ValueStateValues:
            SkipCmdString = '1A{}'.format(ValueStateValues[value])
            self.__SetHelper('Skip', self.makeCmndString(SkipCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSkip')

    def UpdateTrackName(self, value, qualifier):

        trackNum = qualifier['Number']
        if 0 <= trackNum <= 999:
            trackNum = str(trackNum).zfill(4)
            TrackNameCmdString = '59{0}{1}'.format(trackNum[2:], trackNum[:2])
            self.__UpdateHelper('TrackName', self.makeCmndString(TrackNameCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTrackName')

    def __MatchTrackName(self, match, tag):

        qualifier = {}
        numb_val = ''.join([match.group(2).decode(), match.group(1).decode()])
        qualifier['Number'] = int(numb_val)
        value = match.group(3).decode()
        self.WriteStatus('TrackName', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Authenticated in ['Authenticated', 'Not Needed']:
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Authenticated', 'Not Needed']:
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
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):

        self.counter = 0

        self.Error(['Error: Illegal command'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'

    def tasc_31_3294_R(self):

        self.DeviceSelectStates = {
            'SD1' : '00',
            'SD2' : '01',
            'USB' : '10'
        }

        self.DeviceSelectValues = {
            '00' : 'SD1',
            '01' : 'SD2',
            '10' : 'USB'
        }

        self.devicePassword = 'SS-R250N'

    def tasc_31_3294_CDR(self):

        self.DeviceSelectStates = {
            'SD1' : '00',
            'SD2' : '01',
            'USB' : '10',
            'CD'  : '11'
        }
        self.DeviceSelectValues = {
            '00' : 'SD1',
            '01' : 'SD2',
            '10' : 'USB',
            '11' : 'CD'
        }

        self.devicePassword = 'SS-CDR250N'

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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