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
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {
            'ZyPer4K': self.zvee_20_3065_4K,
            'ZyPerUHD': self.zvee_20_3065_others,
            'ZyPerHD': self.zvee_20_3065_others,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoEDIDMode': { 'Status': {}},
            'Join': {'Parameters': ['EncoderId', 'DecoderId', 'Mode'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'RestartDevice': { 'Status': {}},
            'RestartServer': { 'Status': {}},
            'RS232Properties': {'Parameters': ['Id', 'Baud', 'Data Bits', 'Stop Bits', 'Parity'], 'Status': {}},
            'Send': {'Parameters': ['Id', 'Type'], 'Status': {}},
        }
        
        self.Authenticated = 'Not Needed'
            
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Zyper'), self.__MatchSuccess, None)
            self.AddMatchString(re.compile(b'autoEdidMode=(enabled|disabled)'), self.__MatchAutoEDIDMode, None)
   
    def __MatchPassword(self, match, tag):

        self.Authenticated = 'Needed'
        self.SetPassword( None, None)
        
    def SetPassword(self, value, qualifier):

        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchSuccess(self, match, tag):

        self.Authenticated = 'User'
    
    def UpdateAutoEDIDMode(self, value, qualifier):

        AutoEDIDModeCmdString = 'show server config\r\n'
        self.__UpdateHelper('AutoEDIDMode', AutoEDIDModeCmdString, value, qualifier)

    def __MatchAutoEDIDMode(self, match, tag):
        
        value = match.group(1).decode().title()
        self.WriteStatus('AutoEDIDMode', value, None)

    def SetJoin(self, value, qualifier):

        EncoderId = qualifier['EncoderId']
        DecoderId = qualifier['DecoderId']
        Mode = qualifier['Mode']

        if EncoderId and DecoderId and Mode in self.SetJoin_ModeStates:
            JoinCmdString = 'join {} {} {}\r\n'.format(EncoderId, DecoderId, self.SetJoin_ModeStates[Mode])
            self.__SetHelper('Join', JoinCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetJoin')

    def SetPresetRecall(self, value, qualifier):

        if value:
            PresetRecallCmdString = 'run preset {}\r\n'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetRestartDevice(self, value, qualifier):

        Device = value
        if Device:
            RestartDeviceCmdString = 'restart device {}\r\n'.format(Device)
            self.__SetHelper('RestartDevice', RestartDeviceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRestartDevice')

    def SetRestartServer(self, value, qualifier):

        RestartServerCmdString = 'restart server\r\n'
        self.__SetHelper('RestartServer', RestartServerCmdString, value, qualifier)

    def SetRS232Properties(self, value, qualifier):

        BaudStates = ['2400', '9600', '19200', '38400', '57600', '115200']
        DataBitsStates = ['7', '8']
        StopBitsStates = ['1', '2']
        ParityStates = ['Even', 'Odd', 'None']

        Id = qualifier['Id']
        Baud = qualifier['Baud']
        DataBits = qualifier['Data Bits']
        StopBits = qualifier['Stop Bits']
        Parity = qualifier['Parity']

        if Id and Baud in BaudStates and DataBits in DataBitsStates and StopBits in StopBitsStates and Parity in ParityStates:
            RS232PropertiesCmdString = 'set device {} rs232 {} {}-bits {}-stop {}\r\n'.format(Id, Baud, DataBits, StopBits, Parity.lower())
            self.__SetHelper('RS232Properties', RS232PropertiesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRS232Properties')

    def SetSend(self, value, qualifier):

        TypeStates = ['IR', 'RS232']
        Id = qualifier['Id']
        Type = qualifier['Type']
        SendString = value
        if Id and Type in TypeStates and SendString:
            SendCmdString = 'send {} {} {}\r\n'.format(Id, Type.lower(), SendString)
            self.__SetHelper('Send', SendCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSend')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Authenticated in ['User', 'Not Needed'] :
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['User', 'Not Needed'] :
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

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.Authenticated = 'Not Needed'

    def zvee_20_3065_4K(self):

        self.SetJoin_ModeStates = {
            'Analog Audio':     'analogAudio',
            'Fast Switched':    'fastSwitched',
            'Genlocked':        'genlocked',
            'Genlocked Scaled': 'genlockedScaled',
            'HDMI Audio':       'hdmiAudio',
            'Mutliview':        'multiview',
            'Video':            'video',
            'Video Wall':       'videoWall',
            'Window':           'window',
            'USB':              'usb'
        }

    def zvee_20_3065_others(self):

        self.SetJoin_ModeStates = {
            'Analog Audio':     'analogAudio',
            'Fast Switched':    'fastSwitched',
            'HDMI Audio':       'hdmiAudio',
            'Video':            'video',
            'Video Wall':       'videoWall',
            'USB':              'usb'
        }

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