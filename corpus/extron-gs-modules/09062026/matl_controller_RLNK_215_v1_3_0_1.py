# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack

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
        self.deviceUsername = 'user'
        self.devicePassword = 'password'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'PowerOutlet': {'Parameters': ['Cycle Time', 'Outlet Number'], 'Status': {}},
            'PowerOutletStatus': {'Parameters': ['Outlet Number'], 'Status': {}},
        }

        self.Authenticated = False
        self.VerboseSent = False
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x01\x15\xFF'), self.__MatchLogInSuccess, None)
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x00\x14\xFF'), self.__MatchLogInError, None)
            self.AddMatchString(re.compile(b'\xFE\x03\x00\x01\x01\x03\xFF'), self.__MatchPing, None)
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x20[\x10\x12]([\x01\x02])([\x00-\x03])[0-9]{4}[\x00-\xFF]\xFF'), self.__MatchPowerOutletStatus, None)

            self.AddMatchString(re.compile(b'\xFE\x04\x00\x10\x10([\x00-\xFF])[\x00-\xFF]\xFF'), self.__MatchError, None)

    def SetLogin(self, match, tag):

        credentials = bytes(self.deviceUsername, 'ascii') + b'\x7C' + bytes(self.devicePassword, 'ascii')
        if len(credentials) > 50:
            self.Error(['Length of username and password must be less than 50 characters.'])
            return

        DataString = b'\x00\x02\x01' + credentials
        LoginString = b'\xFE' + pack('>B', len(DataString)) + DataString
        LoginCmdString = LoginString + self.CalculateChecksum(LoginString) + b'\xFF'

        self.Send(LoginCmdString)

    def __MatchLogInSuccess(self, match, tag):

        self.Authenticated = True

    def __MatchLogInError(self, match, tag):

        self.Authenticated = False
        self.VerboseSent = False
        self.Error(['Log in failed. Please verify login credentials.'])
        self.SetLogin(None, None)

    def SetVerbose(self, value, qualifier):

        self.Send(b'\xFE\x09\x00\x41\x01\x01\x00\x00\x00\x50\x00\x1A\xFF')

    def SetPong(self, match, tag):

        self.Send(b'\xFE\x03\x00\x01\x10\x12\xFF')

        if self.Authenticated and not self.VerboseSent:
            self.VerboseSent = True
            self.SetVerbose( None, None)

    def __MatchPing(self, match, tag):

        self.SetPong( None, None)

    def CalculateChecksum(self, string):

        return pack('B', sum(string) & 127)

    def SetPowerOutlet(self, value, qualifier):

        CycleTimeConstraints = {
            'Min': 0,
            'Max': 3600
        }

        OutletNumberStates = {
            '1': b'\x01',
            '2': b'\x02'
        }

        PowerOutletStates = {
            'On':       b'\x01',
            'Off':      b'\x00',
            'Cycle':    b'\x02',
        }

        Outlet = OutletNumberStates[qualifier['Outlet Number']]

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = '{:04d}'.format(qualifier['Cycle Time']).encode()
            else:
                CycleTime = b'0000'

            PowerOutletCmdString = b'\xFE\x09\x00\x20\x01' + Outlet + PowerOutletStates[value] + CycleTime
            PowerOutletCmdString += self.CalculateChecksum(PowerOutletCmdString) + b'\xFF'
            self.__SetHelper('PowerOutlet', PowerOutletCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerOutlet')

    def UpdatePowerOutletStatus(self, value, qualifier):

        OutletNumberStates = {
            '1': b'\x01',
            '2': b'\x02'
        }
        
        PowerOutletStatusCmdString = b'\xFE\x04\x00\x20\x02' + OutletNumberStates[qualifier['Outlet Number']]
        PowerOutletStatusCmdString += self.CalculateChecksum(PowerOutletStatusCmdString) + b'\xFF'
        self.__UpdateHelper('PowerOutletStatus', PowerOutletStatusCmdString, value, qualifier)

    def __MatchPowerOutletStatus(self, match, tag):

        OutletNumberStates = {
            b'\x01': '1',
            b'\x02': '2'
        }

        PowerOutletState = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Cycle',
            b'\x03': 'Not Controllable'
        }

        PowerOutlet = OutletNumberStates[match.group(1)]
        value = PowerOutletState[match.group(2)]

        self.WriteStatus('PowerOutletStatus', value, {'Outlet Number': PowerOutlet})
            
    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Authenticated and self.VerboseSent:
            self.Send(commandstring)
        else:
            self.Discard('Invalid Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:          
                self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):
        self.counter = 0

        ErrorState = {
            b'\x01': 'Bad Checksum',
            b'\x02': 'Bad Length',
            b'\x03': 'Escaped Error',
            b'\x04': 'Invalid Command',
            b'\x05': 'Invalid Sub-Command',
            b'\x06': 'Invalid Qty Data Bytes',
            b'\x07': 'Invalid Data Byte Values',
            b'\x08': 'Access Denied (Credentials)',
            b'\x10': 'Unknown',
            b'\x11': 'Access Denied (EPO)'
        }

        if match.group(1) == b'\x08':
            self.Authenticated = False
            self.VerboseSent = False

        self.Error(['An error occurred: {}.'.format(ErrorState[match.group(1)])])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = False
        self.VerboseSent = False

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

    def Connect(self, *args, **kwargs):
        result = super().Connect(*args, **kwargs)
        if result == 'Connected':
            self.SetLogin(None, None)
        return result

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()