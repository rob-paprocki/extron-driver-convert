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
        self.__maxBufferSize = 1024
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'DA2 HD 8K L': self.extr_18_6138_2,
            'DA4 HD 8K L': self.extr_18_6138_4,
            'DA6 HD 8K L': self.extr_18_6138_6,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters':['Output'], 'Status': {}},
            'CECAudioMute': {'Parameters':['Output'], 'Status': {}},
            'CECPower': {'Parameters':['Output'], 'Status': {}},
            'CECShowAsActiveSource': {'Parameters':['Output'], 'Status': {}},
            'CECVolume': {'Parameters':['Output'], 'Status': {}},
            'GlobalAudioMute': { 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'HDCPInputAuthorization': { 'Status': {}},
            'HDCPInputStatus': { 'Status': {}},
            'HDCPOutputStatus': {'Parameters':['Output'], 'Status': {}},
            'InputSignalStatus': { 'Status': {}},
            'OutputFormat': {'Parameters':['Output'], 'Status': {}},
            'OutputSignalStatus': {'Parameters':['Output'], 'Status': {}},
            'VideoMute': {'Parameters':['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True
        self.CECOutputList = []

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt(?P<Output>[1-8])\*(?P<value>[0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Amt(?P<value>[01 ]{2,12})\r\n'), self.__MatchAudioMute, 'Query')
            self.AddMatchString(re.compile(b'Amt(?P<value>[01])\r\n'), self.__MatchAudioMute, 'Global')
            self.AddMatchString(re.compile(b'HdcpE(?P<value>[0-1])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI(?P<value>[012])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO(?P<value>[012 ]{2,12})\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Sig(?P<value>[0-1])\*(?P<output>[0-1 ]{2,12})\r\n'), self.__MatchInputOutputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vtpo(?P<Output>[1-8])\*(?P<value>[1-7])\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(re.compile(b'Vtpo(?P<Output>[1-7 ]{2,12})\r\n'), self.__MatchOutputFormat, 'Query')
            self.AddMatchString(re.compile(b'Vmt(?P<Output>[1-8])\*(?P<value>[0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vmt(?P<value>[0-2 ]{2,12})\r\n'), self.__MatchVideoMute, 'Query')
            self.AddMatchString(re.compile(b'Vmt(?P<value>[0-2])\r\n'), self.__MatchVideoMute, 'Global')
            self.AddMatchString(re.compile(b'E(0[1-3])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def SetVerbose(self, value, qualifier):

        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False 

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Output']) <= self.OutputSize and value in ValueStateValues:
            AudioMuteCmdString = '{0}*{1}Z'.format(qualifier['Output'], ValueStateValues[value])
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
        if tag == 'Query':
            output, states = 1, match.group('value').decode().split()
            for i in states:
                self.WriteStatus('AudioMute', ValueStateValues[i], {'Output': str(output)})
                output += 1
        elif tag == 'Global':
            value = ValueStateValues[match.group('value').decode()]
            i = 1
            while (i <= self.OutputSize):
                self.WriteStatus('AudioMute', value, {'Output': str(i)})
                i+=1
        else:
            qualifier = {}
            qualifier['Output'] = match.group('Output').decode()
            value = ValueStateValues[match.group('value').decode()]
            self.WriteStatus('AudioMute', value, qualifier)

    def SetCECAudioMute(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            if output not in self.CECOutputList: # ensures to only enable once
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))
            CECAudioMuteCmdString = 'wO{}*%44%43DCEC\r'.format(output)
            self.__SetHelper('CECAudioMute', CECAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECAudioMute')

    def SetCECPower(self, value, qualifier):

        ValueStateValues = {
            'On' : '%04',
            'Off' : '%36'
        }

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECPowerCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECPower', CECPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECShowAsActiveSource(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECShowAsActiveSourceCmdString = 'wO{}*\"ShowMe\"DCEC\r'.format(output)
            self.__SetHelper('CECShowAsActiveSource', CECShowAsActiveSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECShowAsActiveSource')

    def SetCECVolume(self, value, qualifier):

        ValueStateValues = {
            'Up' : '%44%41',
            'Down' : '%44%42'
        }

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECVolumeCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECVolume', CECVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECVolume')

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            GlobalAudioMuteCmdString = '{0}Z'.format(ValueStateValues[value])
            self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
            'On with Sync': '2'
        }

        if value in ValueStateValues:
            GlobalVideoMuteCmdString = '{0}B'.format(ValueStateValues[value])
            self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{0}HDCP\r'.format(ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = '\x1BEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('HDCPInputAuthorization', value, None)

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Video detected without HDCP',
            '0': 'No video detected',
            '2': 'Video detected with HDCP'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('HDCPInputStatus', value, None)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            HDCPOutputStatusCmdString = '\x1BOHDCP\r'
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Sink detected, output not encrypted',
            '0': 'No active sink detected',
            '2': 'Sink detected, output encrypted'
        }

        count = 1
        values = match.group('value').decode().split()
        for i in values:
            self.WriteStatus('HDCPOutputStatus', ValueStateValues[i], {'Output': str(count)})
            count += 1

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputOutputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('InputSignalStatus', value, None)

        count = 1
        values = match.group('output').decode().split()
        for i in values:
            self.WriteStatus('OutputSignalStatus', ValueStateValues[i], {'Output': str(count)})
            count += 1

    def SetOutputFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto'                  : '1',
            'DVI RGB 444'           : '2',
            'HDMI RGB Full'         : '3',
            'HDMI RGB Limited'      : '4',
            'HDMI YUV 444 Limited'  : '5',
            'HDMI YUV 422 Limited'  : '6',
            'HDMI YUV 420 Limited'  : '7'
        }

        if 1 <= int(qualifier['Output']) <= self.OutputSize and value in ValueStateValues:
            OutputFormatCmdString = '\x1B{0}*{1}VTPO\r'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormat')

    def UpdateOutputFormat(self, value, qualifier):

        OutputFormatCmdString = 'wVTPO\r'
        self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)

    def __MatchOutputFormat(self, match, tag):

        ValueStateValues = {
            '1': 'Auto',
            '2': 'DVI RGB 444',
            '3': 'HDMI RGB Full',
            '4': 'HDMI RGB Limited',
            '5': 'HDMI YUV 444 Limited',
            '6': 'HDMI YUV 422 Limited',
            '7': 'HDMI YUV 420 Limited'
        }

        if tag == 'Query':
            count = 1
            values = match.group('Output').decode().split()
            for i in values:
                self.WriteStatus('OutputFormat', ValueStateValues[i], {'Output': str(count)})
                count += 1
        else:
            qualifier = {}
            qualifier['Output'] = match.group('Output').decode()
            value = ValueStateValues[match.group('value').decode()]
            self.WriteStatus('OutputFormat', value, qualifier)

    def UpdateOutputSignalStatus(self, value, qualifier):

        OutputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('OutputSignalStatus', OutputSignalStatusCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
            'On with Sync': '2'
        }

        if 1 <= int(qualifier['Output']) <= self.OutputSize and value in ValueStateValues:
            VideoMuteCmdString = '{0}*{1}B'.format(qualifier['Output'], ValueStateValues[value])
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

        if tag == 'Query':
            count = 1
            values = match.group('value').decode().split()
            for i in values:
                self.WriteStatus('VideoMute', ValueStateValues[i], {'Output': str(count)})
                count += 1
        elif tag == 'Global':
            value = ValueStateValues[match.group('value').decode()]
            i = 1
            while (i <= self.OutputSize):
                self.WriteStatus('VideoMute', value, {'Output': str(i)})
                i+=1
        else:
            qualifier = {}
            qualifier['Output'] = match.group('Output').decode()
            value = ValueStateValues[match.group('value').decode()]
            self.WriteStatus('VideoMute', value, qualifier)

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
            '10' : 'Invalid command.',
            '13' : 'Invalid value.',
            '14' : 'Not valid for this configuration.',
            '17' : 'Invalid command for signal type.',
            '24' : 'Privilege Violation.',
            '26' : 'Maximum number of connections exceeded.',
            '28' : 'Bad filename / File not found.'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E'+ value])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.EchoDisabled = True
        self.CECOutputList = []

    def extr_18_6138_2(self):

        self.OutputSize = 2

    def extr_18_6138_4(self):

        self.OutputSize = 4

    def extr_18_6138_6(self):

        self.OutputSize = 6

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