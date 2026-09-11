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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FaderLevel': {'Parameters': ['Index'], 'Status': {}},
            'FaderMute': {'Parameters': ['Index'], 'Status': {}},
            'RecallSnapshot': {'Parameters': ['Parameter Set'], 'Status': {}},
            'Router': {'Parameters': ['Index'], 'Status': {}}
        }

        self.run_mode = False
        self.status_map = {}
        self.invalid_indices = set()

        self.states_map = {
            'FaderMute': {
                '0': 'On',
                '1': 'Off'
            }
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus error "(none|flt|err|wrn).*"\n'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set PROC:Remote/(\d{1,4}) 0 0 (-?\d{1,5}).*\n'), self.__MatchFunction, None)
            self.AddMatchString(re.compile(b'OK get PROC:Remote/(\d{1,4}) 0 0 (-?\d{1,5})\n'), self.__MatchFunction, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus runmode "normal"\n'), self.__MatchRunMode, None)
            self.AddMatchString(re.compile(b'ERROR .* (.*)\n'), self.__MatchError, None)

    def __MatchRunMode(self, match, tag):

        self.run_mode = True

        self.Send('scpmode encoding ascii\n')

        self.Send('scpmode valuetype raw\n')

    def __MatchFunction(self, match, tag):

        index = int(match.group(1).decode())
        if index in self.invalid_indices or index not in self.status_map:
            return

        command = self.status_map[index]
        value = match.group(2).decode()

        qualifier = {
            'Index': index
        }

        if command == 'FaderLevel':
            value = int(value) / 100
            if not (-138.01 <= value <= 10):
                return
        elif command == 'Router':
            value_as_int = int(value)
            if not (0 <= value_as_int <= 256):
                return
        else:
            try:
                value = self.states_map[command][value]
            except:
                return

        self.WriteStatus(command, value, qualifier)

    def add(self, command, index):
        
        if index in self.invalid_indices:
            return False
        elif index in self.status_map:
            if self.status_map[index] == command:
                return True
            del self.status_map[index]
            self.invalid_indices.add(index)
            return False
        else:
            self.status_map[index] = command
            return True

    def UpdateDeviceStatus(self, value, qualifier):

        if not self.run_mode:
            self.Send('devstatus runmode\n')

        DeviceStatusCmdString = 'devstatus error\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'none': 'Normal',
            'err':  'Error',
            'flt':  'Fault',
            'wrn':  'Warning'
        }


        value = ValueStateValues[match.group(1).decode()] 
        self.WriteStatus('DeviceStatus', value, None)

    def SetFaderLevel(self, value, qualifier):

        index = int(qualifier['Index'])

        if 1 <= index <= 1000 and -138.01 <= value <= 10:
            FaderLevelCmdString = 'set PROC:Remote/{i} 0 0 {v}\n'.format(i=index, v=int(value * 100))
            self.__SetHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderLevel')

    def UpdateFaderLevel(self, value, qualifier):

        index = int(qualifier['Index'])

        if 1 <= index <= 1000 and self.add('FaderLevel', index):
            FaderLevelCmdString = 'get PROC:Remote/{i} 0 0\n'.format(i=index)
            self.__UpdateHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFaderLevel')

    def SetFaderMute(self, value, qualifier):

        index = qualifier['Index']

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        if 1 <= index <= 1000 and value in ValueStateValues:
            FaderMuteCmdString = 'set PROC:Remote/{i} 0 0 {v}\n'.format(i=index, v=ValueStateValues[value])
            self.__SetHelper('FaderMute', FaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderMute')

    def UpdateFaderMute(self, value, qualifier):

        index = int(qualifier['Index'])

        if 1 <= index <= 1000 and self.add('FaderMute', index):
            FaderMuteCmdString = 'get PROC:Remote/{i} 0 0\n'.format(i=index)
            self.__UpdateHelper('FaderMute', FaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFaderMute')

    def SetRecallSnapshot(self, value, qualifier):

        parameter_set = qualifier['Parameter Set']

        if 1 <= parameter_set <= 65535 and 1 <= int(value) <= 100:
            RecallSnapshotCmdString = 'ssrecall_ex {} {}\n'.format(parameter_set, int(value))
            self.__SetHelper('RecallSnapshot', RecallSnapshotCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallSnapshot')

    def SetRouter(self, value, qualifier):

        index = qualifier['Index']

        if 1 <= index <= 1000 and 0 <= int(value) <= 256:
            RouterCmdString = 'set PROC:Remote/{i} 0 0 {v}\n'.format(i=index, v=int(value))
            self.__SetHelper('Router', RouterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRouter')

    def UpdateRouter(self, value, qualifier):

        index = int(qualifier['Index'])

        if 1 <= index <= 1048 and self.add('Router', index):
            RouterCmdString = 'get PROC:Remote/{i} 0 0\n'.format(i=index)
            self.__UpdateHelper('Router', RouterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRouter')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.run_mode or self.Unidirectional != 'False':
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or not self.run_mode:
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

        error_map = {
            'UnknownCommand':   'Unknown command',
            'WrongFormat':      'Invalid parameter format',
            'InvalidArgument':  'Invalid argument',
            'UnknownAddress':   'Specified address does not exist',
            'UnknownEventID':   'Specified event ID does not exist',
            'TooLongCommand':   'Command was too long',
            'AccessDenied':     'Device is not in an normal running state',
            'Busy':             'Device is busy',
            'ReadOnly':         'Parameter is read-only',
            'NoPermission':     'No access permission',
            'Overload':         'Too much communication',
            'Overflow':         'Communication has overflowed',
            'TooManyFilters':   'Too many filters',
            'InternalError':    'Internal error',
            'Clipped':          'Command contains more than 1000 characters'
        }

        self.Error(['An error occurred: {}.'.format(error_map.get(match.group(1).decode(), 'Unknown error'))])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Send('devmode normal\n')

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.run_mode = False
        self.status_map = {}
        self.invalid_indices = set()

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