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
        self.devicePassword = '0000'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'InputSource': {'Parameters':['Input'], 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'SignalStatus': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }


        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if 'Serial' not in self.ConnectionType:
            self.CmdDelimiter = '\r\n'
            self.AddMatchString(re.compile(b'PASSWORD:'), self.__MatchPassword, None) # login prompt
            self.AddMatchString(re.compile(b'Hello'), self.__MatchAuthenticated, None) # login success
        else:
            self.CmdDelimiter = '\r'

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):

        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Login failed. Please supply proper password'])
        self.Authenticated = 'None'

    def __MatchAuthenticated(self, match, tag):

        self.Authenticated = 'Authenticated'
        self.PasswdPromptCount = 0
        
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal' : 'NORMAL', 
            'Full'   : 'FULL', 
            'Wide'   : 'WIDE', 
            'Zoom'   : 'ZOOM', 
            'Custom' : 'CUSTOM', 
            'True'   : 'TRUE'
        }

        AspectRatioCmdString = 'CF SCREEN {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'NORMAL' : 'Normal', 
            'FULL'   : 'Full', 
            'WIDE'   : 'Wide', 
            'ZOOM'   : 'Zoom', 
            'CUSTOM' : 'Custom', 
            'TRUE'   : 'True'
        }

        AspectRatioCmdString = 'CR SCREEN{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'CF KEYEMU AUTOPC{}'.format(self.CmdDelimiter)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off'   : 'NONE', 
            'Mode 1' : 'RC', 
            'Mode 2' : 'KEY'
        }

        ExecutiveModeCmdString = 'CF KEYDIS {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'NONE' : 'Off', 
            'RC'   : 'Mode 1', 
            'KEY'  : 'Mode 2'
        }

        ExecutiveModeCmdString = 'CR KEYDIS{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF'
        }

        FreezeCmdString = 'CF FREEZE {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF' : 'Off'
        }

        FreezeCmdString = 'CR FREEZE{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInputSource(self, value, qualifier):

        InputStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        ValueStateValues = {
            'Digital' : 'DIGITAL', 
            'Analog'  : 'ANALOG', 
            'Video'   : 'VIDEO', 
            'S-Video' : 'S-VIDEO', 
            'YPbPr'   : 'YPBPR', 
            'YCbCr'   : 'YCBCR', 
            'SDI 1'   : 'SDI1', 
            'SDI 2'   : 'SDI2', 
            'SCART'   : 'HDCP', 
            'HDCP'    : 'SCART', 
            'HDMI'    : 'HDMI'
        }

        input_ = qualifier['Input']
        InputSourceCmdString = 'CF INPUT{0} {1}{2}'.format(InputStates[input_], ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)

    def UpdateInputSource(self, value, qualifier):

        ValueStateValues = {
            'DIGITAL' : 'Digital', 
            'ANALOG'  : 'Analog', 
            'VIDEO'   : 'Video', 
            'S-VIDEO' : 'S-Video', 
            'YPBPR'   : 'YPbPr', 
            'SDI1'    : 'SDI 1', 
            'SDI2'    : 'SDI 2', 
            'SCART'   : 'SCART', 
            'HDCP'    : 'HDCP', 
            'HDMI'    : 'HDMI',
            'NOCARD'  : 'No Input Board',
        }

        input_ = qualifier['Input']
        InputCmdString = 'CR SRCINP{0}{1}'.format(input_, self.CmdDelimiter)
        res = self.__UpdateHelper('InputSource', InputCmdString, value, qualifier)
        if res:
            try:
                source = ValueStateValues[res[4:-1]]
                self.WriteStatus('InputSource', source, {'Input': input_})
            except (KeyError, IndexError):
                self.Error(['Input Source: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : 'NORMAL', 
            'Eco 1'  : 'ECO1', 
            'Eco 2'  : 'ECO2', 
            'Auto'   : 'AUTO'
        }

        LampModeCmdString = 'CF AUTOLAMPCONTRL {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            'NORMAL' : 'Normal', 
            'ECO1'   : 'Eco 1', 
            'ECO2'   : 'Eco 2', 
            'AUTO'   : 'Auto'
        }

        LampModeCmdString = 'CR AUTOLAMPCONTRL{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                lamp_values = re.search('000 (\d+) (\d+)[ ]?(\d+)?[ ]?(\d+)?\r', res)
                if lamp_values:
                    for index in range(len(lamp_values.groups())):
                        if lamp_values.groups()[index]:
                            self.WriteStatus('LampUsage', int(lamp_values.groups()[index]), {'Lamp' : str(index + 1)})
                else:
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Right' : 'RIGHT', 
            'Left'  : 'LEFT', 
            'Up'    : 'UP', 
            'Down'  : 'DN', 
            'Enter' : 'SELECT'
        }

        MenuNavigationCmdString = 'CF KEYEMU {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF'
        }

        OnScreenDisplayCmdString = 'CF MENU {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF', 
        }

        PowerCmdString = 'CF POWER {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        PowerStatusValues = {
            '00' : 'On', 
            '80' : 'Off', 
            '40' : 'Warming Up',
            '20' : 'Cooling Down',
            '28' : 'Cooling Down',
            '24' : 'Cooling Down',
            '21' : 'Cooling Down',
            '2C' : 'Cooling Down',
        }

        DeviceStatusValues = {
            '00' : 'Normal', 
            '80' : 'Normal', 
            '40' : 'Normal',
            '20' : 'Normal',
            '10' : 'Power Fail', 
            '28' : 'Process Cooling Down (Abnormal Temperature)', 
            '88' : 'Standby after Cooling Down (Abnormal Temp)', 
            '24' : 'Processing Power Save (Cooling Down)', 
            '04' : 'Power Save', 
            '21' : 'Cooling Down (Lamp Failure)', 
            '81' : 'Standby after Cooling Down (Lamp Failure)', 
            '2C' : 'Cooling Down (Shutter Mgmt)', 
            '8C' : 'Standby after Cooling Down (Shutter Mgmt)'
        }

        PowerCmdString = 'CR STATUS{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                power_value = PowerStatusValues.get(res[4:-1], 'Off')
                dev_value = DeviceStatusValues[res[4:-1]]
                self.WriteStatus('Power', power_value, qualifier)
                self.WriteStatus('DeviceStatus', dev_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateSignalStatus(self, value, qualifier):

        ValueStateValues = {
            'ON' : 'Signal Available', 
            'OFF' : 'No Signal'
        }

        SignalStatusCmdString = 'CR SIGNAL{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('SignalStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Signal Status: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF'
        }

        VideoMuteCmdString = 'CF VMUTE {0}{1}'.format(ValueStateValues[value], self.CmdDelimiter)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF' : 'Off'
        }

        VideoMuteCmdString = 'CR VMUTE{}'.format(self.CmdDelimiter)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?'  : 'Parameter designation error',
            '101': 'Function not available in the selected Mode',
            '102': 'Selected value not in range',
            '103': 'Command mismatched to hardware',
            '201': 'Values are beyond upper or lower limits',
            '301': 'Not executable due to screen capturing process',
            '402': 'Not executable due to PIN code in operation',
        }

        if response:
            if response[:-1] in DEVICE_ERROR_CODES:
                self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[:-1]])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Authenticated', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command , res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

