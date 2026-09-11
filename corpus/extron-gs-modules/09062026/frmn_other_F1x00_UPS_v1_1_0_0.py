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
        self.Models = {
            'F1000-UPS': self.frmn_31_533_F1000,
            'F1500-UPS': self.frmn_31_533_F1500,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutomaticVoltageRegulation': { 'Status': {}},
            'BatteryLevelStatus': { 'Status': {}},
            'CurrentOutputStatus': { 'Status': {}},
            'LoadLevelStatus': { 'Status': {}},
            'OutletControl': {'Parameters': ['Bank'], 'Status': {}},
            'PowerStatus': { 'Status': {}},
            'Reset': { 'Status': {}},
            'VoltageInputStatus': { 'Status': {}},
            'VoltageOutputStatus': { 'Status': {}},
            'VoltageRMSStatus': { 'Status': {}},
            'VoltageVAStatus': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\$AVR = (STANDARD|SENSITIVE|OFF)\r'), self.__MatchAutomaticVoltageRegulation, None)
            self.AddMatchString(re.compile(b'\$BATTERY = (\d{1,3})\r'), self.__MatchBatteryLevelStatus, None)
            self.AddMatchString(re.compile(b'\$CURRENT = (\d{1,3})\r'), self.__MatchCurrentOutputStatus, None)
            self.AddMatchString(re.compile(b'\$LOAD = (\d{1,3})\r'), self.__MatchLoadLevelStatus, None)
            self.AddMatchString(re.compile(b'\$PWR = (NORMAL|OVERVOLTAGE|UNDERVOLTAGE|LOST POWER|TEST)\r'), self.__MatchPowerStatus, None)
            self.AddMatchString(re.compile(b'\$VOLTS_IN = (\d{1,3})\r'), self.__MatchVoltageInputStatus, None)
            self.AddMatchString(re.compile(b'\$VOLTS_OUT = (\d{1,3})\r'), self.__MatchVoltageOutputStatus, None)
            self.AddMatchString(re.compile(b'\$WATTS = (\d{1,3})\r'), self.__MatchVoltageRMSStatus, None)
            self.AddMatchString(re.compile(b'\$VA = (\d{1,3})\r'), self.__MatchVoltageVAStatus, None)

            self.AddMatchString(re.compile(b'\$INVALID_PARAMETER\r'), self.__MatchError, None)

    def SetAutomaticVoltageRegulation(self, value, qualifier):

        ValueStateValues = [
            'Standard',
            'Sensitive',
            'Off'
        ]

        if value in ValueStateValues:
            AutomaticVoltageRegulationCmdString = '!SET_AVR {}\r'.format(value.upper())
            self.__SetHelper('AutomaticVoltageRegulation', AutomaticVoltageRegulationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomaticVoltageRegulation')

    def UpdateAutomaticVoltageRegulation(self, value, qualifier):

        AutomaticVoltageRegulationCmdString = '?LIST_CONFIG\r'
        self.__UpdateHelper('AutomaticVoltageRegulation', AutomaticVoltageRegulationCmdString, value, qualifier)

    def __MatchAutomaticVoltageRegulation(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutomaticVoltageRegulation', value, None)

    def UpdateBatteryLevelStatus(self, value, qualifier):

        BatteryLevelStatusCmdString = '?BATTERYSTAT\r'
        self.__UpdateHelper('BatteryLevelStatus', BatteryLevelStatusCmdString, value, qualifier)

    def __MatchBatteryLevelStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BatteryLevelStatus', value, None)

    def UpdateCurrentOutputStatus(self, value, qualifier):

        CurrentOutputStatusCmdString = '?CURRENT\r'
        self.__UpdateHelper('CurrentOutputStatus', CurrentOutputStatusCmdString, value, qualifier)

    def __MatchCurrentOutputStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('CurrentOutputStatus', value, None)

    def UpdateLoadLevelStatus(self, value, qualifier):

        LoadLevelStatusCmdString = '?LOADSTAT\r'
        self.__UpdateHelper('LoadLevelStatus', LoadLevelStatusCmdString, value, qualifier)

    def __MatchLoadLevelStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LoadLevelStatus', value, None)

    def SetOutletControl(self, value, qualifier):

        bank = qualifier['Bank']

        ValueStateValues = [
            'On',
            'Off'
        ]

        if bank in self.SetOutletControl_BankStates and value in ValueStateValues:
            if bank == 'All':
                OutletControlCmdString = '!ALL_{}\r'.format(value.upper())
            else:
                OutletControlCmdString = '!SWITCH {} {}\r'.format(bank, value.upper())

            self.__SetHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutletControl')

    def UpdateOutletControl(self, value, qualifier):

        bank = qualifier['Bank']

        if bank in self.UpdateOutletControl_BankStates:
            OutletControlCmdString = '?OUTLETSTAT\r'
            self.__UpdateHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletControl')

    def __MatchOutletControl(self, match, tag):

        qualifier = {
            'Bank': match.group(1).decode()
        }

        value = match.group(2).decode().title()
        self.WriteStatus('OutletControl', value, qualifier)

    def UpdatePowerStatus(self, value, qualifier):

        PowerStatusCmdString = '?POWERSTAT\r'
        self.__UpdateHelper('PowerStatus', PowerStatusCmdString, value, qualifier)

    def __MatchPowerStatus(self, match, tag):

        ValueStateValues = {
            'NORMAL':       'Normal Operation',
            'OVERVOLTAGE':  'Overvoltage',
            'UNDERVOLTAGE': 'Undervoltage',
            'LOST POWER':   'Lost Power',
            'TEST':         'Test Mode'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerStatus', value, None)

    def SetReset(self, value, qualifier):

        ResetCmdString = '!RESET_ALL\r'
        self.__SetHelper('Reset', ResetCmdString, value, qualifier)

    def UpdateVoltageInputStatus(self, value, qualifier):

        VoltageInputStatusCmdString = '?POWER\r'
        self.__UpdateHelper('VoltageInputStatus', VoltageInputStatusCmdString, value, qualifier)

    def __MatchVoltageInputStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VoltageInputStatus', value, None)

    def UpdateVoltageOutputStatus(self, value, qualifier):

        self.UpdateVoltageInputStatus(value, qualifier)

    def __MatchVoltageOutputStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VoltageOutputStatus', value, None)

    def UpdateVoltageRMSStatus(self, value, qualifier):

        self.UpdateVoltageInputStatus(value, qualifier)

    def __MatchVoltageRMSStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VoltageRMSStatus', value, None)

    def UpdateVoltageVAStatus(self, value, qualifier):

        self.UpdateVoltageInputStatus(value, qualifier)

    def __MatchVoltageVAStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VoltageVAStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

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

        self.Error(['Invalid Parameter'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def frmn_31_533_F1000(self):

        self.SetOutletControl_BankStates = [
            '1',
            '2',
            'All'
        ]

        self.UpdateOutletControl_BankStates = [
            '1',
            '2'
        ]

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile('\$BANK({}) = (ON|OFF)\r'.format('|'.join(self.UpdateOutletControl_BankStates)).encode(encoding='iso-8859-1')), self.__MatchOutletControl, None)

    def frmn_31_533_F1500(self):

        self.SetOutletControl_BankStates = [
            '1',
            '2',
            '3',
            '4',
            'All'
        ]

        self.UpdateOutletControl_BankStates = [
            '1',
            '2',
            '3',
            '4'
        ]

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile('\$BANK({}) = (ON|OFF)\r'.format('|'.join(self.UpdateOutletControl_BankStates)).encode(encoding='iso-8859-1')), self.__MatchOutletControl, None)

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