from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait

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
            'AudioInputFormat': {'Parameters':['Input'], 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoswitchMode': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Input'], 'Status': {}},
            'HDCPOutputStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'VideoMute': { 'Status': {}},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'AfmtI(?P<Input>[1-2])\*(?P<value>[0-2])\r\n'), self.__MatchAudioInputFormat, None)
            self.AddMatchString(re.compile(b'AfmtI(?P<value1>[0-2]) (?P<value2>[0-2])\r\n'), self.__MatchAudioInputFormat, 'All')
            self.AddMatchString(re.compile(b'Amt(?P<value>[0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Ausw(?P<value>[0-2])\r\n'), self.__MatchAutoswitchMode, None)
            self.AddMatchString(re.compile(b'HdcpE(?P<Input>[1-2])\*(?P<value>[0-1])\r\n'), self.__MatchHDCPInputAuthorization, 'Set')
            self.AddMatchString(re.compile(b'HdcpE(?P<value1>[0-1]) (?P<value2>[0-1])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI(?P<Input>[1-2]) (?P<value>[0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO(?P<value>[0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'In(?P<value>[1-2]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sig(?P<value1>[0-1]) (?P<value2>[0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vmt(?P<value>[0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)                 
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioInputFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Digital': '1',
            'Analog': '2'
        }

        if 1 <= int(qualifier['Input']) <= 2 and value in ValueStateValues:
            AudioInputFormatCmdString = 'wI{0}*{1}AFMT\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputFormat')

    def UpdateAudioInputFormat(self, value, qualifier):

        AudioInputFormatCmdString = 'wIAFMT\r'
        self.__UpdateHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def __MatchAudioInputFormat(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Digital',
            '2': 'Analog'
        }

        qualifier = {}

        if tag == 'All':
            in1 = ValueStateValues[match.group('value1').decode()]
            self.WriteStatus('AudioInputFormat', in1, {"Input": '1'})
            in2 = ValueStateValues[match.group('value2').decode()]
            self.WriteStatus('AudioInputFormat', in2, {"Input": '2'})
        else:
            qualifier['Input'] = match.group('Input').decode()
            value = ValueStateValues[match.group('value').decode()]
            self.WriteStatus('AudioInputFormat', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '{0}Z'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoswitchMode(self, value, qualifier):

        ValueStateValues = {
            'Highest Active Input': '1',
            'Lowest Active Input': '2',
            'Off': '0'
        }

        if value in ValueStateValues:
            AutoswitchModeCmdString = 'w{0}AUSW\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoswitchMode', AutoswitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoswitchMode')

    def UpdateAutoswitchMode(self, value, qualifier):

        AutoswitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoswitchMode', AutoswitchModeCmdString, value, qualifier)

    def __MatchAutoswitchMode(self, match, tag):

        ValueStateValues = {
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('AutoswitchMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Input']) <= 2 and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = 'wEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if tag == 'Set':
            qualifier = {}
            qualifier['Input'] = match.group('Input').decode()
            value = ValueStateValues[match.group('value').decode()]
            self.WriteStatus('HDCPInputAuthorization', value, qualifier)
        else:
            in1 = ValueStateValues[match.group('value1').decode()]
            in2 = ValueStateValues[match.group('value2').decode()]
            self.WriteStatus('HDCPInputAuthorization', in1, {"Input": '1'})
            self.WriteStatus('HDCPInputAuthorization', in2, {"Input": '2'})

    def UpdateHDCPInputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 2:
            HDCPInputStatusCmdString = 'wIHDCP\r'
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Device Detected',
            '1': 'Source Detected with HDCP',
            '2': 'Source Detected without HDCP'
        }

        qualifier = {}
        qualifier['Input'] = match.group('Input').decode()
        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sink Device Detected',
            '1': 'Sink Detected with HDCP',
            '2': 'Sink Detected without HDCP'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1' : '1!', 
            '2' : '2!'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group('value').decode()
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'wLS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        in1 = ValueStateValues[match.group('value1').decode()]
        in2 = ValueStateValues[match.group('value2').decode()]
        self.WriteStatus('InputSignalStatus', in1, {"Input": '1'})
        self.WriteStatus('InputSignalStatus', in2, {"Input": '2'})

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'On with Sync': '2',
            'Off': '0'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = '{}B'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('VideoMute', value, None)

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

    
    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid Input Number',
            '06' : 'Invalid Channel Change',
            '10' : 'Invalid Command',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode()])

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

