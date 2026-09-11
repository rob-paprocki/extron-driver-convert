from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self.Models = {
            'RLNK-SW620R': self.matl_20_1046_620,
            'RLNK-SW715R': self.matl_20_1046_715,
            'RLNK-SW620R-NS': self.matl_20_1046_620,
            'RLNK-SW715R-NS': self.matl_20_1046_715,
            'ECB2SP-RLNK': self.matl_20_1046_620,
            'ECB2S-RLNK': self.matl_20_1046_620,
            'RLNK-SW220-NS': self.matl_20_1046_220,
            'RLNK-SW215-NS': self.matl_20_1046_220,
            'RLNK-SW815R_SP': self.matl_20_1046_815,
            'RLNK-SW415R_SP': self.matl_20_1046_415,
            }
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentRMSLoad': { 'Status': {}},
            'CurrentWattage': { 'Status': {}},
            'DryContacts': {'Parameters':['Contact Number','Cycle Time'], 'Status': {}},
            'DryContacts220': {'Parameters':['Cycle Time'], 'Status': {}},
            'DryContactsStatus': {'Parameters':['Contact Number'], 'Status': {}},
            'DryContactsStatus220': { 'Status': {}},
            'PeakVoltage': { 'Status': {}},
            'PowerOutlet': {'Parameters':['Outlet Number','Cycle Time'], 'Status': {}},
            'PowerOutlet220': {'Parameters':['Cycle Time'], 'Status': {}},
            'PowerOutletStatus': {'Parameters':['Outlet Number'], 'Status': {}},
            'RMSVoltage': { 'Status': {}},
            'Temperature': { 'Status': {}},
            'ThermalLoad': { 'Status': {}}, 
            }

        self.VerboseDisabled = True
        self.Authenticated = False  
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE\x07\x00\x54\x10([0-9]{2}\.[0-9])([\x00-\xFF])\xFF'), self.__MatchCurrentRMSLoad, None)
            self.AddMatchString(re.compile(b'\xFE\x07\x00\x56\x10([0-9]{4})([\x00-\xFF])\xFF'), self.__MatchCurrentWattage, None)
            self.AddMatchString(re.compile(b'\xFE\x03\x00\x01\x01\x03\xFF'), self.__MatchPing, None)            
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x30(\x10|\x12)([\x01-\x04])([\x00-\x03])([0-9]{1,4})([\x00-\xFF])\xFF'), self.__MatchDryContactsStatus, None)
            self.AddMatchString(re.compile(b'\xFE\x06\x00\x51\x10([0-9]{1,3})([\x00-\xFF])\xFF'), self.__MatchPeakVoltage, None)
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x20(\x10|\x12)([\x01-\x08])([\x00-\x03])([0-9]{1,4})([\x00-\xFF])\xFF'), self.__MatchPowerOutletStatus, None)
            self.AddMatchString(re.compile(b'\xFE\x06\x00\x52\x10([0-9]{1,3})([\x00-\xFF])\xFF'), self.__MatchRMSVoltage, None)
            self.AddMatchString(re.compile(b'\xFE\x06\x00\x55\x10([0-9]{1,3})([\x00-\xFF])\xFF'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'\xFE\x06\x00\x58\x10([0-9]{1,4}\.[0-9])([\x00-\xFF])\xFF'), self.__MatchThermalLoad, None)
            self.AddMatchString(re.compile(b'\xFE([\x01-\xFF])\x00\x10([\x00-\x11])[\x00-\xFF]{1,2}\xFF'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x00\x14\xFF'), self.__MatchLoginError, None)
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x01\x15\xFF'), self.__MatchLoginSuccess, None)
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x41\x10\x01\x01\x00\x00\x00\x00\x5A\xFF'), self.__MatchVerbose, None)

    def SetLogin(self, match, tag):

        credentials = bytes(self.deviceUsername, 'ascii') + b'\x7C' + bytes(self.devicePassword, 'ascii')
        if len(credentials) > 50:
            self.Error(['Length of username and password must be less than 50 characters.'])
            return
        DataString = b'\x00\x02\x01' + credentials
        Length = pack('>B', len(DataString))
        LoginString = b'\xFE' + Length + DataString
        CheckSum = self.CalculateChecksum(LoginString)
        LoginCmdString = LoginString + CheckSum + b'\xFF'
        self.Send(LoginCmdString)

    def SetPong(self, match, tag):

        self.Send(b'\xFE\x03\x00\x01\x10\x12\xFF')
        if self.Authenticated and self.VerboseDisabled:
            self.VerboseDisabled = False
            self.SetVerbose( None, None)

    def __MatchPing(self, match, tag):
        
        self.SetPong( None, None)

    def __MatchLoginError(self, match, tag):

        self.Authenticated = False
        self.VerboseDisabled = True
        self.Error(['Login Failed'])
        self.SetLogin(None, None)

    def __MatchLoginSuccess(self, match, tag):

        self.Authenticated = True

    def SetVerbose(self, value, qualifier):
        self.Send(b'\xFE\x09\x00\x41\x01\x01\x00\x00\x00\x50\x00\x1A\xFF')

    def __MatchVerbose(self, match, tag):
       
        self.VerboseDisabled = False

    def CalculateChecksum(self, string):
        CheckSum = 0 
        for i in string:
            CheckSum = CheckSum + i
        if CheckSum > 255:
            CheckSum = CheckSum & 255
        CheckSum = pack('B', CheckSum & 127)
        return CheckSum

    def UpdateCurrentRMSLoad(self, value, qualifier):

        CurrentRMSLoadCmdString = b'\xFE\x04\x00\x54\x02\x00\x58\xFF'
        self.__UpdateHelper('CurrentRMSLoad', CurrentRMSLoadCmdString, value, qualifier)

    def __MatchCurrentRMSLoad(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('CurrentRMSLoad', value, None)

    def UpdateCurrentWattage(self, value, qualifier):

        CurrentWattageCmdString = b'\xFE\x04\x00\x56\x02\x00\x5A\xFF'
        self.__UpdateHelper('CurrentWattage', CurrentWattageCmdString, value, qualifier)

    def __MatchCurrentWattage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('CurrentWattage', value, None)

    def SetDryContacts(self, value, qualifier):

        CycleTimeConstraints = {
            'Min' : 0,
            'Max' : 3600
            }

        DryContactStateValues = {
            'On'    : b'\x01', 
            'Off'   : b'\x00', 
            'Cycle' : b'\x02'
        }

        Contact = self.ContactNumberStates[qualifier['Contact Number']]

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = bytes(str(qualifier['Cycle Time']).zfill(4), 'ascii')
            else:
                CycleTime = b'0000'
            DryContacts = b'\xFE\x09\x00\x30\x01' + Contact + DryContactStateValues[value] + CycleTime
            CheckSum = self.CalculateChecksum(DryContacts)
            DryContactsCmdString = DryContacts + CheckSum + b'\xFF'
            self.__SetHelper('DryContacts', DryContactsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDryContacts')

    def SetDryContacts220(self, value, qualifier):

        CycleTimeConstraints = {
            'Min' : 0,
            'Max' : 3600
            }

        DryContactStateValues = {
            'On'    : b'\x01', 
            'Off'   : b'\x00', 
            'Cycle' : b'\x02'
        }

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = bytes(str(qualifier['Cycle Time']).zfill(4), 'ascii')
            else:
                CycleTime = b'0000'
            DryContacts = b'\xFE\x09\x00\x30\x01\x01' + DryContactStateValues[value] + CycleTime
            CheckSum = self.CalculateChecksum(DryContacts)
            DryContacts220CmdString = DryContacts + CheckSum + b'\xFF'
            self.__SetHelper('DryContacts220', DryContacts220CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDryContacts220')

    def UpdateDryContactsStatus(self, value, qualifier):
        
        DryContactsStatus = b'\xFE\x04\x00\x30\x02' + self.ContactNumberStates[qualifier['Contact Number']]
        CheckSum = self.CalculateChecksum(DryContactsStatus)
        DryContactsStatusCmdString = DryContactsStatus + CheckSum + b'\xFF'
        self.__UpdateHelper('DryContactsStatus', DryContactsStatusCmdString, value, qualifier)

    def __MatchDryContactsStatus(self, match, tag):

        DryContactValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off', 
            b'\x02' : 'Cycle',
            b'\x03' : 'Not Controllable'
        }

        ContactNumber = self.ContactNumberStatesName[match.group(2)]
        value = DryContactValues[match.group(3)]
        self.WriteStatus('DryContactsStatus', value, {'Contact Number': ContactNumber})

    def UpdateDryContactsStatus220(self, value, qualifier):

        DryContactsStatus = b'\xFE\x04\x00\x30\x02\x01'
        CheckSum = self.CalculateChecksum(DryContactsStatus)
        DryContactsStatus220CmdString = DryContactsStatus + CheckSum + b'\xFF'
        self.__UpdateHelper('DryContactsStatus220', DryContactsStatus220CmdString, value, qualifier)

    def __MatchDryContactsStatus220(self, match, tag):

        DryContactValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off', 
            b'\x02' : 'Cycle',
            b'\x03' : 'Not Controllable'
        }

        value = DryContactValues[match.group(3)]
        self.WriteStatus('DryContactsStatus220', value, None)

    def UpdatePeakVoltage(self, value, qualifier):

        PeakVoltageCmdString = b'\xFE\x04\x00\x51\x02\x00\x55\xFF'
        self.__UpdateHelper('PeakVoltage', PeakVoltageCmdString, value, qualifier)

    def __MatchPeakVoltage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('PeakVoltage', value, None)

    def SetPowerOutlet(self, value, qualifier):

        CycleTimeConstraints = {
            'Min' : 0,
            'Max' : 3600
            }

        PowerOutletStateValues = {
            'On'    : b'\x01', 
            'Off'   : b'\x00', 
            'Cycle' : b'\x02'
        }

        Outlet = self.OutletNumberStates[qualifier['Outlet Number']]

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = bytes(str(qualifier['Cycle Time']).zfill(4), 'ascii')
            else:
                CycleTime = b'0000'
            PowerOutlet = b'\xFE\x09\x00\x20\x01' + Outlet + PowerOutletStateValues[value] + CycleTime
            CheckSum = self.CalculateChecksum(PowerOutlet)
            PowerOutletCmdString = PowerOutlet + CheckSum + b'\xFF'
            self.__SetHelper('PowerOutlet', PowerOutletCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerOutlet')

    def SetPowerOutlet220(self, value, qualifier):

        CycleTimeConstraints = {
            'Min' : 0,
            'Max' : 3600
            }

        PowerOutletStateValues = {
            'On'    : b'\x01', 
            'Off'   : b'\x00', 
            'Cycle' : b'\x02'
        }

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = bytes(str(qualifier['Cycle Time']).zfill(4), 'ascii')
            else:
                CycleTime = b'0000'
            PowerOutlet = b'\xFE\x09\x00\x20\x01\x02' + PowerOutletStateValues[value] + CycleTime
            CheckSum = self.CalculateChecksum(PowerOutlet)
            PowerOutlet220CmdString = PowerOutlet + CheckSum + b'\xFF'
            self.__SetHelper('PowerOutlet220', PowerOutlet220CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerOutlet220')

    def UpdatePowerOutletStatus(self, value, qualifier):        

        PowerOutletStatus = b'\xFE\x04\x00\x20\x02' + self.OutletNumberStates[qualifier['Outlet Number']]
        CheckSum = self.CalculateChecksum(PowerOutletStatus)
        PowerOutletStatusCmdString = PowerOutletStatus + CheckSum + b'\xFF'
        self.__UpdateHelper('PowerOutletStatus', PowerOutletStatusCmdString, value, qualifier)

    def __MatchPowerOutletStatus(self, match, tag):
        
        PowerOutletStatusStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off', 
            b'\x02' : 'Cycle',
            b'\x03' : 'Not Controllable'
        }

        PowerOutletStatus = self.OutletNumberStatesName[match.group(2)]
        value = PowerOutletStatusStateValues[match.group(3)]
        self.WriteStatus('PowerOutletStatus', value, {'Outlet Number':PowerOutletStatus})

    def UpdateRMSVoltage(self, value, qualifier):

        RMSVoltageCmdString = b'\xFE\x04\x00\x52\x02\x00\x56\xFF'
        self.__UpdateHelper('RMSVoltage', RMSVoltageCmdString, value, qualifier)

    def __MatchRMSVoltage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('RMSVoltage', value, None)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = b'\xFE\x04\x00\x55\x02\x00\x59\xFF'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def UpdateThermalLoad(self, value, qualifier):

        ThermalLoadCmdString = b'\xFE\x04\x00\x58\x02\x00\x5C\xFF'
        self.__UpdateHelper('ThermalLoad', ThermalLoadCmdString, value, qualifier)

    def __MatchThermalLoad(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('ThermalLoad', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
            
        if (self.Authenticated and not self.VerboseDisabled):
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

        ErrorCode = {
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
        if match.group(1) == b'\x08':
            self.Authenticated = False
            self.VerboseDisabled = True
        self.Error([ErrorCode[match.group(2)]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetLogin(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = False
        self.VerboseDisabled = True

    def matl_20_1046_815(self):
        self.ContactNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02'
        }
        self.ContactNumberStatesName = {
           b'\x01':'1', 
           b'\x02':'2'
        }

        self.OutletNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06', 
            '7' : b'\x07',
            '8' : b'\x08'
        }
        self.OutletNumberStatesName = {
          b'\x01' : '1',
          b'\x02' : '2', 
          b'\x03' : '3', 
          b'\x04' : '4', 
          b'\x05' : '5', 
          b'\x06' : '6', 
          b'\x07' : '7',
          b'\x08' : '8'
        }

    def matl_20_1046_715(self):
        self.ContactNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03',
            '4' : b'\x04'
        }
        self.ContactNumberStatesName = {
           b'\x01' : '1', 
           b'\x02' : '2', 
           b'\x03' : '3',
           b'\x04' : '4'   
        }

        self.OutletNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06', 
            '7' : b'\x07'
        }
        self.OutletNumberStatesName = {
          b'\x01' : '1', 
          b'\x02' : '2', 
          b'\x03' : '3', 
          b'\x04' : '4', 
          b'\x05' : '5', 
          b'\x06' : '6', 
          b'\x07' : '7'
        }

    def matl_20_1046_620(self):
        self.ContactNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03',
            '4' : b'\x04'
        }
        self.ContactNumberStatesName = {
           b'\x01' : '1', 
           b'\x02' : '2', 
           b'\x03' : '3',
           b'\x04' : '4'  
        }

        self.OutletNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06'
        }
        self.OutletNumberStatesName = {
          b'\x01' : '1', 
          b'\x02' : '2', 
          b'\x03' : '3', 
          b'\x04' : '4', 
          b'\x05' : '5', 
          b'\x06' : '6'
        }

    def matl_20_1046_415(self):
        self.ContactNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02'
        }
        self.ContactNumberStatesName = {
           b'\x01' : '1', 
           b'\x02' : '2'
        }

        self.OutletNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04'
        }
        self.OutletNumberStatesName = {
          b'\x01' : '1',
          b'\x02' : '2', 
          b'\x03' : '3', 
          b'\x04' : '4'
        }

    def matl_20_1046_220(self):
        self.OutletNumberStates = {
            '1' : b'\x01', 
            '2' : b'\x02'
        }
        self.OutletNumberStatesName = {
          b'\x01' : '1',
          b'\x02' : '2'
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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

