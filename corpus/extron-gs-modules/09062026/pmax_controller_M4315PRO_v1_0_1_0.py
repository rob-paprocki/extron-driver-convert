# Copyright 2026, Extron. All rights reserved.

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
            'All': { 'Status': {}},
            'GreenButton': { 'Status': {}},
            'Outlet': {'Parameters':['Output'], 'Status': {}},
            'PowerStatus': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'Reset': { 'Status': {}},
            'Trigger': {'Parameters':['Output'], 'Status': {}}
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\$OUTLET1 = (ON|OFF)\r\$OUTLET2 = (ON|OFF)\r\$OUTLET3 = (ON|OFF)\r\$OUTLET4 = (ON|OFF)\r\$OUTLET5 = (ON|OFF)\r\$OUTLET6 = (ON|OFF)\r\$OUTLET7 = (ON|OFF)\r\$OUTLET8 = (ON|OFF)\r'), self.__MatchOutlet, None)
            self.AddMatchString(re.compile(b'\$PWR = (RECOVERY|NORMAL|OVERVOLTAGE|UNDERVOLTAGE)\r\n'), self.__MatchPowerStatus, None)

    def SetAll(self, value, qualifier):

        AllState = {
            'On'    : '!ALL_ON\r', 
            'Off'   : '!ALL_OFF\r'
            }

        AllCmdString = AllState[value]
        self.__SetHelper('All', AllCmdString, value, qualifier)

    def SetGreenButton(self, value, qualifier):

        GreenButtonCmdString = '!GREEN_BUTTON\r'
        self.__SetHelper('GreenButton', GreenButtonCmdString, value, qualifier)

    def SetOutlet(self, value, qualifier):

        OutletState = {
            'On'    : 'ON', 
            'Off'   : 'OFF'
            }

        OutputValue = qualifier['Output']
        if 1 <= int(OutputValue) <= 8:
            OutletCmdString = '!SWITCH {0} {1}\r'.format(OutputValue, OutletState[value])
            self.__SetHelper('Outlet', OutletCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutlet')

    def UpdateOutlet(self, value, qualifier):
            
        OutletCmdString = '?OUTLETSTAT\r'
        self.__UpdateHelper('Outlet', OutletCmdString, value, qualifier)

    def __MatchOutlet(self, match, tag):

        OutletState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value1 = OutletState[match.group(1).decode()]
        self.WriteStatus('Outlet', value1, {'Output' : '1'})

        value2 = OutletState[match.group(2).decode()]
        self.WriteStatus('Outlet', value2, {'Output' : '2'})

        value3 = OutletState[match.group(3).decode()]
        self.WriteStatus('Outlet', value3, {'Output' : '3'})

        value4 = OutletState[match.group(4).decode()]
        self.WriteStatus('Outlet', value4, {'Output' : '4'})

        value5 = OutletState[match.group(5).decode()]
        self.WriteStatus('Outlet', value5, {'Output' : '5'})

        value6 = OutletState[match.group(6).decode()]
        self.WriteStatus('Outlet', value6, {'Output' : '6'})

        value7 = OutletState[match.group(7).decode()]
        self.WriteStatus('Outlet', value7, {'Output' : '7'})

        value8 = OutletState[match.group(8).decode()]
        self.WriteStatus('Outlet', value8, {'Output' : '8'})

    def UpdatePowerStatus(self, value, qualifier):

        PowerStatusCmdString = '?POWERSTAT\r'
        self.__UpdateHelper('PowerStatus', PowerStatusCmdString, value, qualifier)

    def __MatchPowerStatus(self, match, tag):

        PowerStatusState = {
            'NORMAL' : 'Normal', 
            'OVERVOLTAGE' : 'Over Voltage', 
            'UNDERVOLTAGE' : 'Under Voltage', 
            'RECOVERY' : 'Recovery'
            }

        value = PowerStatusState[match.group(1).decode()]
        self.WriteStatus('PowerStatus', value, None)

    def SetReboot(self, value, qualifier):

        RebootState = {
            '1' : '!REBOOT_1\r', 
            '2' : '!REBOOT_2\r'
            }

        RebootCmdString = RebootState[value]
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)
    def SetReset(self, value, qualifier):

        ResetCmdString = '!RESET_ALL\r'
        self.__SetHelper('Reset', ResetCmdString, value, qualifier)
    def SetTrigger(self, value, qualifier):

        TriggerState = {
            'None' : 'NONE', 
            'Button 1' : 'BUTTON_1', 
            'Button 2' : 'BUTTON_2', 
            'Both Buttons' : 'BUTTON_GREEN', 
            'DC Input Trigger' : 'TRIGIN'
            }

        OutputValue = qualifier['Output']
        if 1 <= int(OutputValue) <= 8:
            TriggerCmdString = '!SET_TRIGGER {0} {1}\r'.format(OutputValue, TriggerState[value])
            self.__SetHelper('Trigger', TriggerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrigger')

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

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()