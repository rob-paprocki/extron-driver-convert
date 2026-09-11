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
        self._SystemAddress = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExtractedAudioOutput': { 'Status': {}},
            'ExtractedAudioOutputMode': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'InputTieStatus': {'Parameters':['Input','Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters':['Output'], 'Status': {}},
            'OutputVideoMode': { 'Status': {}},
            'RefreshMatrix': { 'Status': {}},
            'SignalStatus': {'Parameters':['Input'], 'Status': {}},
            'Stream': {'Parameters':['Output'], 'Status': {}},
            'SwitchMode': { 'Status': {}},
        }

        self.initialized = False # For Serial Connection
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'EXA BTV OUT(1|2)\r\n'), self.__MatchExtractedAudioOutput, None)
            self.AddMatchString(re.compile(b'OUT0 EXA (EN|DIS)\r\n'), self.__MatchExtractedAudioOutputMode, None)
            self.AddMatchString(re.compile(b'F/W Version : (\d+?\.\d+?) +?=='), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'OUT1 VS IN([1-4])\r\nOUT2 VS IN([1-4])\r\n'), self.__MatchRefreshMatrix, None)
            self.AddMatchString(re.compile(b'OUT1 VIDEO(1|2)\r\n'), self.__MatchOutputVideoMode, None)
            self.AddMatchString(re.compile(b'IN([1-4]) SIG STA (0|1)\r\n'), self.__MatchSignalStatus, None)
            self.AddMatchString(re.compile(b'OUT([0-2]) STREAM (ON|OFF)\r\n'), self.__MatchStream, None)
            self.AddMatchString(re.compile(b'SWITCH MODE(0|1)\r\n'), self.__MatchSwitchMode, None)
            self.AddMatchString(re.compile(b'CMD ERR'), self.__MatchError, None)

    @property
    def SystemAddress(self):
        return self._SystemAddress

    @SystemAddress.setter
    def SystemAddress(self, value):
        if value == 'Single':
            self._SystemAddress = '00'
        elif 1 <= int(value) <= 99:
            self._SystemAddress = value.zfill(2)
        else:
            print('Invalid System Address.')

    def InitSystAddr(self, value, qualifier):

        self.Send('SET ADDR {0}\r'.format(self._SystemAddress))
        self.initialized = True

    def SetExtractedAudioOutput(self, value, qualifier):

        ValueStateValues = ['1', '2']
        if value in ValueStateValues:
            ExtractedAudioOutputCmdString = 'A{0}SET EXA BTV OUT{1}\r'.format(self._SystemAddress, value)
            self.__SetHelper('ExtractedAudioOutput', ExtractedAudioOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExtractedAudioOutput')

    def UpdateExtractedAudioOutput(self, value, qualifier):

        ExtractedAudioOutputCmdString = 'A{0}GET EXA BTV OUT\r'.format(self._SystemAddress)
        self.__UpdateHelper('ExtractedAudioOutput', ExtractedAudioOutputCmdString, value, qualifier)

    def __MatchExtractedAudioOutput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ExtractedAudioOutput', value, None)

    def SetExtractedAudioOutputMode(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'EN', 
            'Disable' : 'DIS'
        }

        ExtractedAudioOutputModeCmdString = 'A{0}SET OUT0 EXA {1}\r'.format(self._SystemAddress, ValueStateValues[value])
        self.__SetHelper('ExtractedAudioOutputMode', ExtractedAudioOutputModeCmdString, value, qualifier)

    def UpdateExtractedAudioOutputMode(self, value, qualifier):

        ExtractedAudioOutputModeCmdString = 'A{0}GET OUT0 EXA\r'.format(self._SystemAddress)
        self.__UpdateHelper('ExtractedAudioOutputMode', ExtractedAudioOutputModeCmdString, value, qualifier)

    def __MatchExtractedAudioOutputMode(self, match, tag):

        ValueStateValues = {
            'EN'  : 'Enable', 
            'DIS' : 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExtractedAudioOutputMode', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):


        FirmwareVersionCmdString = 'A{0}STA\r'.format(self._SystemAddress)
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        
        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetMatrixTieCommand(self, value, qualifier):

        InputStates = ['1', '2', '3', '4']

        OutputStates = {
            '1'   : '1', 
            '2'   : '2', 
            'All' : '0'
        }

        input_val = qualifier['Input']
        output_val = qualifier['Output']
        if input_val in InputStates and output_val in OutputStates:
            MatrixTieCommandCmdString = 'A{0}SET OUT{1} VS IN{2}\r'.format(self._SystemAddress, OutputStates[output_val], input_val)
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetOutputVideoMode(self, value, qualifier):

        ValueStateValues = {
            'Bypass'   : '1', 
            '4K to 2K' : '2'
        }

        OutputVideoModeCmdString = 'A{0}SET OUT1 VIDEO{1}\r'.format(self._SystemAddress, ValueStateValues[value])
        self.__SetHelper('OutputVideoMode', OutputVideoModeCmdString, value, qualifier)

    def UpdateOutputVideoMode(self, value, qualifier):

        OutputVideoModeCmdString = 'A{0}GET OUT1 VIDEO\r'.format(self._SystemAddress)
        self.__UpdateHelper('OutputVideoMode', OutputVideoModeCmdString, value, qualifier)

    def __MatchOutputVideoMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Bypass', 
            '2' : '4K to 2K'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputVideoMode', value, None)

    def SetRefreshMatrix(self, value, qualifier):

        RefreshMatrixCmdString = 'A{0}GET OUT0 VS\r'.format(self._SystemAddress)
        self.__SetHelper('RefreshMatrix', RefreshMatrixCmdString, value, qualifier)

    def __MatchRefreshMatrix(self, match, tag):

        output_list = ['1', '2']
        input_list = [match.group(1).decode(), match.group(2).decode()]
        for i in range(len(output_list)):
            self.WriteStatus('OutputTieStatus', input_list[i], {'Output' : output_list[i]})
            self.WriteStatus('InputTieStatus', 'Tied', {'Input' : input_list[i], 'Output' : output_list[i]})
            for inp in range (1, 5):
                if inp != int(input_list[i]):
                    self.WriteStatus('InputTieStatus', 'Untied', {'Input': str(inp), 'Output': output_list[i]})

    def UpdateSignalStatus(self, value, qualifier):

        input_val = qualifier['Input']
        if input_val in ['1', '2', '3', '4']:
            SignalStatusCmdString = 'A{0}GET IN{1} SIG STA\r'.format(self._SystemAddress, input_val)
            self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSignalStatus')

    def __MatchSignalStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Inactive'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SignalStatus', value, qualifier)

    def SetStream(self, value, qualifier):

        OutputStates = {
            '1'   : '1', 
            '2'   : '2', 
            'All' : '0'
        }

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF'
        }

        output_val = qualifier['Output']
        if output_val in OutputStates:
            StreamCmdString = 'A{0}SET OUT{1} STREAM {2}\r'.format(self._SystemAddress, OutputStates[output_val], ValueStateValues[value])
            self.__SetHelper('Stream', StreamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStream')

    def UpdateStream(self, value, qualifier):

        OutputStates = {
            '1'   : '1', 
            '2'   : '2', 
        }
        
        output_val = qualifier['Output']
        if output_val in OutputStates:
            StreamCmdString = 'A{0}GET OUT{1} STREAM\r'.format(self._SystemAddress, OutputStates[output_val])
            self.__UpdateHelper('Stream', StreamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStream')

    def __MatchStream(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }
        
        value = ValueStateValues[match.group(2).decode()]
        
        if match.group(1).decode() == 0:
            self.WriteStatus('Stream', value, {'Output' : '1'})
            self.WriteStatus('Stream', value, {'Output' : '2'})
        else:
            qualifier = {}
            qualifier['Output'] = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Stream', value, qualifier)

    def SetSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Single' : '0', 
            'Double' : '1'
        }

        SwitchModeCmdString = 'A{0}SET SWITCH MODE{1}\r'.format(self._SystemAddress, ValueStateValues[value])
        self.__SetHelper('SwitchMode', SwitchModeCmdString, value, qualifier)

    def UpdateSwitchMode(self, value, qualifier):

        SwitchModeCmdString = 'A{0}GET SWITCH MODE\r'.format(self._SystemAddress)
        self.__UpdateHelper('SwitchMode', SwitchModeCmdString, value, qualifier)

    def __MatchSwitchMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Single', 
            '1' : 'Double'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SwitchMode', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if 'Serial' in self.ConnectionType and self.initialized == False:
            self.InitSystAddr(None, None)
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

        self.Error(['Command Error.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetRefreshMatrix(None, None)
    
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