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
            'Cycle': { 'Status': {}},
            'Event': {'Parameters': ['Event'], 'Status': {}},
            'Outlet': { 'Status': {}},
            'Reboot': { 'Status': {}},
        }

        self.authenticated = False

        self.event_regex = re.compile('([1-8])\.[\s\S]+?(On|Off|Cycle)[\s\S]+?\r\n')  

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'get cycle\r\n(\d+)\r\nOk'), self.__MatchCycle, None)
            self.AddMatchString(re.compile(b'get events\r\n([\s\S]+?)\r\nOk'), self.__MatchEvent, None)
            self.AddMatchString(re.compile(b'get outlet\r\n(On|Off|Cycling)\r\nOk'), self.__MatchOutlet, None)

            self.AddMatchString(re.compile(b'\xFF\xFB\x01'), self.__MatchHandshake, None)
            self.AddMatchString(re.compile(b'User>'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password>'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Axess Ready>?'), self.__MatchAuthenticated, None)

            self.AddMatchString(re.compile(b'(Invalid Command|Bad command or parameter)'), self.__MatchError, None)

    def __MatchHandshake(self, match, tag):

        self.Send(b'\xFF\xFD\x01\xFF\xFD\x03\xFF\xFB\x1F\xFF\xFB\x18\xFF\xFB\x20')

        self.authenticated = False

    def __MatchUsername(self, match, tag):

        self.Send('admin\r\n')

    def __MatchPassword(self, match, tag):

        self.Send(self.devicePassword + '\r\n')

    def __MatchAuthenticated(self, match, tag):

        self.authenticated = True
    
    def SetCycle(self, value, qualifier):

        if 1 <= value <= 999:
            CycleCmdString = 'set cycle {}\r\n'.format(value)
            self.__SetHelper('Cycle', CycleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCycle')

    def UpdateCycle(self, value, qualifier):

        CycleCmdString = 'get cycle\r\n'
        self.__UpdateHelper('Cycle', CycleCmdString, value, qualifier)

    def __MatchCycle(self, match, tag):

        value = int(match.group(1).decode())

        if 1 <= value <= 999:
            self.WriteStatus('Cycle', value, None)

    def SetEvent(self, value, qualifier):

        event = int(qualifier['Event'])

        ValueStateValues = [
            'On',
            'Off',
            'Cycle'
        ]

        if 1 <= event <= 8 and value in ValueStateValues:
            EventCmdString = 'set event {} action {}\r\n'.format(event, value.lower())
            self.__SetHelper('Event', EventCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEvent')

    def UpdateEvent(self, value, qualifier):

        event = int(qualifier['Event'])

        if 1 <= event <= 8:
            EventCmdString = 'get events\r\n'
            self.__UpdateHelper('Event', EventCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEvent')

    def __MatchEvent(self, match, tag):

        for event, value in self.event_regex.findall(match.group(1).decode()):
            self.WriteStatus('Event', value, {'Event': event})

    def SetOutlet(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off',
            'Cycle'
        ]

        if value in ValueStateValues:
            OutletCmdString = 'set outlet {}\r\n'.format(value.lower())
            self.__SetHelper('Outlet', OutletCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutlet')

    def UpdateOutlet(self, value, qualifier):

        OutletCmdString = 'get outlet\r\n'
        self.__UpdateHelper('Outlet', OutletCmdString, value, qualifier)

    def __MatchOutlet(self, match, tag):

        ValueStateValues = {
            'On':       'On',
            'Off':      'Off',
            'Cycling':  'Cycle'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Outlet', value, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'reboot\r\n'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.authenticated:
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.authenticated:
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

        self.Error(['An error occurred: {}.'.format(match.group(1).decode())])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.authenticated = False

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