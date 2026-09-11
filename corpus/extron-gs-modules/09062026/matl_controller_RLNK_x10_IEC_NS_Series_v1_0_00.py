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
        self.devicePassword = 'user'
        self.Models = {
            'RLNK-210-IEC-NS': self.matl_20_17349_2,
            'RLNK-410R-IEC-NS': self.matl_20_17349_4,
            'RLNK-910R-IEC-NS': self.matl_20_17349_8
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'OutletControl': {'Parameters':['Outlet','Cycle Time'], 'Status': {}},
            'OutletStatus': {'Parameters':['Outlet'], 'Status': {}},
            'SequencePowerOutlets': {'Parameters':['Delay Time'], 'Status': {}},
            'SequencePowerOutletsStatus': { 'Status': {}}
        }

        self.authenticated = False
        self.VerboseDisabled = True


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x20[\x10\x12]([\x01-\x08])([\x00\x01])\d{4}[\x00-\xFF]\xFF'), self.__MatchOutletStatus, None)
            self.AddMatchString(re.compile(b'\xFE\x08\x00\x36([\x10\x12])([\x00-\x04])\d{4}[\x00-\xFF]\xFF'), self.__MatchSequencePowerOutletsStatus, None)
        
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x10\x10([\x01-\x11])[\x00-\xFF]\xFF'), self.__MatchError, None)

            self.AddMatchString(re.compile(b'\xFE\x03\x00\x01\x01\x03\xFF'), self.__MatchPing, None)

            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x01\x15\xFF'), self.__MatchLogin, True)
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x00\x14\xFF'), self.__MatchLogin, False)

            self.AddMatchString(re.compile(b'\xFE\x09\x00\x41\x10\x01\x04\x00\x00\x00\x00\x5D\xFF'), self.__MatchVerbose, None)

    def __MatchPing(self, match, tag):

        self.Send(b'\xFE\x03\x00\x01\x10\x12\xFF')

    def SetLogin(self, value, qualifier):

        string = b'\x00\x02\x01user|' + self.devicePassword.encode(encoding='iso-8859-1')
        length = pack('>B', len(string))
        self.Send(self.checksum(b'\xFE' + length + string))
    
    def __MatchLogin(self, match, tag):

        self.authenticated = tag
        if not tag:
            self.Error(['Authentication failed. Please verify password.'])

    def SetVerbose(self, value, qualifier):

        self.Send(b'\xFE\x09\x00\x41\x01\x01\x04\x00\x00\x00\x00\x4E\xFF')

    def __MatchVerbose(self, match, tag):

        self.VerboseDisabled = False

    def checksum(self, string):

        return string + bytes([sum(string) & 0x7F]) + b'\xFF'
    
    def SetOutletControl(self, value, qualifier):

        outlet = int(qualifier['Outlet'])
        cycle_time = qualifier['Cycle Time']

        ValueStateValues = {
            'On'    : b'\x01',
            'Off'   : b'\x00',
            'Cycle' : b'\x02'
        }

        if 1 <= outlet <= self.outlets and 0 <= cycle_time <= 3600 and value in ValueStateValues:
            if value != 'Cycle':
                cycle_time = 0

            OutletControlCmdString = self.checksum(b'\xFE\x09\x00\x20\x01' + bytes([outlet]) + ValueStateValues[value] + '{:04d}'.format(cycle_time).encode())
            self.__SetHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutletControl')

    def UpdateOutletStatus(self, value, qualifier):

        outlet = int(qualifier['Outlet'])

        if 1 <= outlet <= self.outlets:
            OutletStatusCmdString = self.checksum(b'\xFE\x04\x00\x20\x02' + bytes([outlet]))
            self.__UpdateHelper('OutletStatus', OutletStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletStatus')

    def __MatchOutletStatus(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On',
            b'\x00' : 'Off'
        }

        qualifier = {
            'Outlet' : str(match.group(1)[0])
        }

        value = ValueStateValues[match.group(2)]
        self.WriteStatus('OutletStatus', value, qualifier)

    def SetSequencePowerOutlets(self, value, qualifier):

        delay_time = qualifier['Delay Time']
        
        ValueStateValues = {
            'Up'    : b'\x01',
            'Down'  : b'\x03'
        }

        if 0 <= delay_time <= 999 and value in ValueStateValues:
            SequencePowerOutletsCmdString = self.checksum(b'\xFE\x08\x00\x36\x01' + ValueStateValues[value] + '{:04d}'.format(delay_time).encode())
            self.__SetHelper('SequencePowerOutlets', SequencePowerOutletsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequencePowerOutlets')

    def UpdateSequencePowerOutletsStatus(self, value, qualifier):

        SequencePowerOutletsStatusCmdString = b'\xFE\x04\x00\x36\x02\x00\x3A\xFF'
        self.__UpdateHelper('SequencePowerOutletsStatus', SequencePowerOutletsStatusCmdString, value, qualifier)

    def __MatchSequencePowerOutletsStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Not Sequencing',
            b'\x01': 'Sequencing Up',
            b'\x02': 'Sequence Up Complete',
            b'\x03': 'Sequencing Down',
            b'\x04': 'Sequence Down Complete'
        }

        value = ValueStateValues[match.group(2)]
        self.WriteStatus('SequencePowerOutletsStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or not self.authenticated:
            self.Discard('Inappropriate Command ' + command)
        elif not self.authenticated:
            self.SetLogin(None, None)
        else:
            if not self.VerboseDisabled:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                
                self.Send(commandstring)
            else:
                self.SetVerbose(None, None)

    def __MatchError(self, match, tag):

        self.counter = 0

        error_map = {
            b'\x01' : 'Bad Checksum',
            b'\x02' : 'Bad Length',
            b'\x03' : 'Escaped Error',
            b'\x04' : 'Invalid Command',
            b'\x05' : 'Invalid Sub-Command',
            b'\x06' : 'Invalid Qty Data Bytes',
            b'\x07' : 'Invalid Data Byte Values',
            b'\x08' : 'Access Denied (Credentials)',
            b'\x10' : 'Unknown',
            b'\x11' : 'Access Denied (EPO)'
        }

        self.Error([error_map[match.group(1)]])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.authenticated = False
        self.VerboseDisabled = True

    def matl_20_17349_2(self):

        self.outlets = 2

    def matl_20_17349_4(self):

        self.outlets = 4

    def matl_20_17349_8(self):

        self.outlets = 8

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