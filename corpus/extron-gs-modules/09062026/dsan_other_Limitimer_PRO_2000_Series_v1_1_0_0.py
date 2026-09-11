from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Clear': {'Status': {}},
            'LargeSignalLightClockAdjustment': { 'Status': {}},
            'LargeSignalLightTimeUpdates': { 'Status': {}},
            'LEDStatus': {'Parameters':['LED'], 'Status': {}},
            'Options': {'Status': {}},
            'Programs': {'Status': {}},
            'RemainingTimeStatus': {'Parameters':['Mode'], 'Status': {}},
            'SetSeconds': {'Status': {}},
            'StartStop': {'Status': {}},
            'SumUpTime': {'Status': {}},
            'SumUpTimeStatus': {'Status': {}},
            'TotalTime': {'Status': {}},
            'TotalTimeStatus': {'Status': {}}
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\>(P1|P2|P3|SES|BP|BK|GRN|YEL|RED|SM)(LED)?(ON|DM|OF) \w\w\r'), self.__MatchLEDStatus, None)
            self.AddMatchString(re.compile(b'\>(RTSTR|RTSTRSZ)=\s?(\d+:\d+) \w\w\r'), self.__MatchRemainingTimeStatus, None)
            self.AddMatchString(re.compile(b'\>STSTR=\s?(\d+:\d+) \w\w\r'), self.__MatchSumUpTimeStatus, None)
            self.AddMatchString(re.compile(b'\>TTSTR=\s?(\d+:\d+) \w\w\r'), self.__MatchTotalTimeStatus, None)

    def SetClear(self, value, qualifier):

        ClearCmdString = '>CLR 01\r'
        self.__SetHelper('Clear', ClearCmdString, value, qualifier)

    def SetLargeSignalLightClockAdjustment(self, value, qualifier):

        ValueStateValues = {
            'Increment Hours' : '>INCHOUR 38\r', 
            'Increment Minutes' : '>INCMIN DE\r'
        }

        if value in ValueStateValues:
            LargeSignalLightClockAdjustmentCmdString = ValueStateValues[value]
            self.__SetHelper('LargeSignalLightClockAdjustment', LargeSignalLightClockAdjustmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLargeSignalLightClockAdjustment')

    def SetLargeSignalLightTimeUpdates(self, value, qualifier):

        ValueStateValues = {
            'Enable' : '>ENTIME E2\r', 
            'Disable' : '>DISTIME 2F\r'
        }

        if value in ValueStateValues:
            LargeSignalLightTimeUpdatesCmdString = ValueStateValues[value]
            self.__SetHelper('LargeSignalLightTimeUpdates', LargeSignalLightTimeUpdatesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLargeSignalLightTimeUpdates')

    def __MatchLEDStatus(self, match, tag):

        LEDStates = {
            'P1' : 'Program 1', 
            'P2' : 'Program 2', 
            'P3' : 'Program 3', 
            'SES': 'Session', 
            'BP' : 'Beep', 
            'BK' : 'Blink', 
            'GRN': 'Green', 
            'YEL': 'Yellow', 
            'RED': 'Red', 
            'SM' : 'Seconds Mode Indicator' 
        }

        ValueStateValues = {
            'ON' : 'On', 
            'DM' : 'Dim', 
            'OF' : 'Off'
        }

        ProgramsStates = {
            'P1' : '1', 
            'P2' : '2', 
            'P3' : '3', 
            'SES': 'Session'
        }

        qualifier = {'LED': LEDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('LEDStatus', value, qualifier)

        if match.group(1).decode() in ['P1','P2','P3', 'SES'] and value in ['On','Dim']:
            programValue = ProgramsStates[match.group(1).decode()]
            self.WriteStatus('Programs', programValue, None)

    def SetOptions(self, value, qualifier):

        ValueStateValues = {
            'Beep' : '>BEEP 3C\r', 
            'Blink' : '>BLNK 47\r', 
            'Repeat' : '>REPT 5B\r'
        }

        if value in ValueStateValues:
            OptionsCmdString = ValueStateValues[value]
            self.__SetHelper('Options', OptionsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOptions')

    def SetPrograms(self, value, qualifier):

        ValueStateValues = {
            '1' : '>PRG1 3A\r', 
            '2' : '>PRG2 3B\r', 
            '3' : '>PRG3 3C\r', 
            'Session' : '>SESS 5E\r'
        }

        if value in ValueStateValues:
            ProgramsCmdString = ValueStateValues[value]
            self.__SetHelper('Programs', ProgramsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPrograms')

    def __MatchRemainingTimeStatus(self, match, tag):

        ModeStates = {
            'RTSTR': 'Count Up',
            'RTSTRSZ': 'Count Down'
        }

        qualifier = {'Mode': ModeStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('RemainingTimeStatus', value, qualifier)

    def SetSetSeconds(self, value, qualifier):

        SetSecondsCmdString = '>SSEC 4E\r'
        self.__SetHelper('SetSeconds', SetSecondsCmdString, value, qualifier)

    def SetStartStop(self, value, qualifier):

        StartStopCmdString = '>STOP 66\r'
        self.__SetHelper('StartStop', StartStopCmdString, value, qualifier)

    def SetSumUpTime(self, value, qualifier):

        ValueStateValues = {
            'Up' : '>STUP 6C\r', 
            'Down' : '>STDN 59\r'
        }

        if value in ValueStateValues:
            SumUpTimeCmdString = ValueStateValues[value]
            self.__SetHelper('SumUpTime', SumUpTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSumUpTime')

    def __MatchSumUpTimeStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SumUpTimeStatus', value, None)

    def SetTotalTime(self, value, qualifier):

        ValueStateValues = {
            'Up' : '>TTUP 6D\r',
            'Down' : '>TTDN 5A\r'
        }

        if value in ValueStateValues:
            TotalTimeCmdString = ValueStateValues[value]
            self.__SetHelper('TotalTime', TotalTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTotalTime')

    def __MatchTotalTimeStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TotalTimeStatus', value, None)

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