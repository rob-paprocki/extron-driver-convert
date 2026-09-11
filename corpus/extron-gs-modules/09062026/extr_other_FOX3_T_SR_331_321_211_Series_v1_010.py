# Copyright 2025, Extron. All rights reserved.

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioFormat': { 'Status': {}},
            'FiberLinkStatus': {'Parameters':['SFP Optical Module'], 'Status': {}},
            'InputSignalStatus': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'AfmtI([1-2])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(re.compile(b'Inf00\*SFPALnk([0-1]) SFPBLnk([0-1]) SigI([0-1]) HdcpI([0-2]) HdcpO([0-2]) AudI([0-2]) (TX|RX) (SM|MM)\r\n'), self.__MatchFiberLinkStatus, 'Query')
            self.AddMatchString(re.compile(b'Sts02\*([1-2])\*([0-1])\r\n'), self.__MatchFiberLinkStatus, 'Unsolicited')
            self.AddMatchString(re.compile(b'Sts04\*([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'SigI([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Mut([0-1]+)\r\n'), self.__MatchVideoMute, 'Query')
            self.AddMatchString(re.compile(b'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, 'VideoUnsolicited')
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, 'VideoGlobal')
            self.AddMatchString(re.compile(b'Vol(\d{1,3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()        
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetAudioFormat(self, value, qualifier):

        ValueStateValues={
            'Digital': '1',
            'Analog': '2',
        }
        if value in ValueStateValues:
            AudioFormatCmdString = '\x1bI{0}AFMT\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        self.__UpdateHelper('AudioFormat', '\x1bIAFMT\r', value, qualifier)

    def __MatchAudioFormat(self, match, tag):

        ValueStateValues = {
            '1' : 'Digital',
            '2': 'Analog'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioFormat', value, None)

    def UpdateFiberLinkStatus(self, value, qualifier):

        FiberLinkStatusCmdString = 'i'
        self.__UpdateHelper('FiberLinkStatus', FiberLinkStatusCmdString, value, qualifier)

    def __MatchFiberLinkStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'Not Active',
            '1' : 'Active',
        }

        qualifierstate = {
            '1': 'SFP A',
            '2': 'SFP B'
        }

        if tag == 'Query':
            self.WriteStatus('FiberLinkStatus', ValueStateValues[match.group(1).decode()], {'SFP Optical Module': 'SFP A'})
            self.WriteStatus('FiberLinkStatus', ValueStateValues[match.group(2).decode()], {'SFP Optical Module': 'SFP B'})
        else:
            self.WriteStatus('FiberLinkStatus', ValueStateValues[match.group(2).decode()], {'SFP Optical Module': qualifierstate[match.group(1).decode()]})

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusStatusCmdString = '4s'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'Not Active',
            '1' : 'Active',
        }

        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(1).decode()], None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues={
            'On': '1',
            'Off': '0',
            'On with Sync': '2'
        }
        if value in ValueStateValues:
            VideoMuteCmdString = '{0}B'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'On with Sync'

        }

        self.WriteStatus('VideoMute', ValueStateValues[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.__SetHelper('Volume', '{0}v'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'v', value, qualifier)

    def __MatchVolume(self, match, qualifier):

        self.WriteStatus('Volume', int(match.group(1)), None)

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

        DEVICE_ERROR_CODES = {
            '10': 'Invalid Command',
            '11': 'Invalid preset number',
            '13': 'Invalid parameter',
            '14': 'Invalid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System or command timed out',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad file name or file not found',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E'+ match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
