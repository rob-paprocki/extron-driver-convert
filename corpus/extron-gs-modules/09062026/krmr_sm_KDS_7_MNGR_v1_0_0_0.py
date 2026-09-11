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
        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'RouteCommand': {'Parameters':['Type', 'Encoder ID', 'Decoder ID'], 'Status': {}}
        }

        self.LoginCount = 0
        self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'~01@LOCK-FP ([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'ERR ([0-9]+)\r\n'), self.__MatchError, None)

            self.AddMatchString(re.compile('~01@LOGIN {0},{1},OK\r\n'.format(self.deviceUsername, self.devicePassword).encode()), self.__MatchLoginSuccess, None)

    def __QueueLogin(self):
        if self.deviceUsername and self.devicePassword:
            self.Login(None, None)
            self.LoginCount += 1
            if self.LoginCount > 1:
                self.Error(['Login failed']) 
        else:
            self.Authenticated = True

    def Login(self, value, qualifier):

        self.Send('#LOGIN {0},{1}\r'.format(self.deviceUsername, self.devicePassword))

    def __MatchLoginSuccess(self, match, tag):

        self.Authenticated = True

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '#LOCK-FP {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = '#LOCK-FP?\r'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetRouteCommand(self, value, qualifier):

        TypeStates = {
            'Video': 'video',
            'Audio': 'audio',
            'USB': 'usb',
            'IR': 'ir',
            'RS-232': 'rs232',
            'CEC': 'cec',
            'All': 'all'
        }

        encoder_id = qualifier['Encoder ID']
        decoder_id = qualifier['Decoder ID']
        if qualifier['Type'] in TypeStates:
            RouteCommandCmdString = '#KDS-ROUTE {0},[{1},{2}]\r'.format(TypeStates[qualifier['Type']], encoder_id, decoder_id)
            self.__SetHelper('RouteCommand', RouteCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRouteCommand')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated:
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
            self.__QueueLogin()
            #self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):

        self.counter = 0

        DEVICE_ERROR_CODES = {
            0: 'No error',
            1: 'Protocol syntax',
            2: 'Command not available',
            3: 'Parameter out of range',
            4: 'Unauthorized access',
            5: 'Internal firmware error',
            6: 'Protocol busy',
            7: 'Wrong CRC',
            8: 'Timeout',
            9: 'Reserved',
            10: 'Not enough space for data (firmware, FPGA...)',
            11: 'Not enough space - file system',
            12: 'File does not exist',
            13: 'File cannot be created',
            14: 'File cannot open',
            15: 'Feature not supported',
            16: 'Reserved',
            17: 'Reserved',
            18: 'Reserved',
            19: 'Reserved',
            20: 'Reserved',
            21: 'Packet CRC error',
            22: 'Packet number not expected (missing packet)',
            23: 'Packet size wrong',
            24: 'Reserved',
            25: 'Reserved',
            26: 'Reserved',
            27: 'Reserved',
            28: 'Reserved',
            29: 'Reserved',
            30: 'EDID corrupted',
            31: 'Device specific errors',
            32: 'File has same CRC - not changed',
            33: 'Wrong operation mode',
            34: 'Device/chip not initialized',
            35: 'Device not available'
        }

        err_code = int(match.group(1).decode())
        if err_code in DEVICE_ERROR_CODES:
            err_msg = DEVICE_ERROR_CODES[err_code]
            if err_msg == 'Unauthorized access':
                self.Authenticated = False
            self.Error([err_msg])
        else:
            self.Error(['Unknown error code: {}'.format(err_code)])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.LoginCount = 0
        self.Authenticated = False

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()