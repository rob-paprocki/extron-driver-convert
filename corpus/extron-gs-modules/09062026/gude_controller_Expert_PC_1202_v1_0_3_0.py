# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self, deviceUsername=None, devicePassword=None):

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
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AirPressureStatus': { 'Status': {}},
            'CurrentStatus': { 'Status': {}},
            'DewPointStatus': { 'Status': {}},
            'DewPointTemperatureDifferenceStatus': { 'Status': {}},
            'HumidityStatus': { 'Status': {}},
            'Power': {'Parameters':['Port'], 'Status': {}},
            'PowerActiveStatus': { 'Status': {}},
            'ResidualCurrentStatus': { 'Status': {}},
            'TemperatureStatus': { 'Status': {}},
            'TotalActiveEnergyStatus': { 'Status': {}},
            'VoltageStatus': { 'Status': {}}
        }

        self.Authentication = 'Not Needed'

        self.PowerListRegEx = re.compile(r'P([1-4])=(ON|OFF)')
        self.ProbeValuesRegEx = re.compile(r'([01345])="(\d*(?:\.\d+)?).+?"')
        ap_regex_str = 'L=1,L=\".*?\",0=\"(\d+?\.?\d*?)(k?Wh)\",1=\"(\d+?\.?\d*?)W\",2=\"(\d+?\.?\d*?)V\",3=\"(\d+?\.?\d*?)A\",21=\"(\d+?\.?\d*?)A\"\r\n>'
        self.ActivePowerRegEx = re.compile(ap_regex_str)
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\r\nConsole login: '), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'\r\nPassword: '), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'\r\nLogin accepted.\r\n>'), self.__MatchPasswordSuccessful, None)
            self.AddMatchString(re.compile(b'\r\nLogin failed.\r\n>'), self.__MatchPasswordFailure, None)

    def __MatchUsername(self, match, tag):

        self.SetUsername( None, None)
        self.Authentication = False

    def SetUsername(self, value, qualifier):

        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):

        self.SetPassword( None, None)

    def __MatchPasswordSuccessful(self, match, tag):

        self.Authentication = True

    def __MatchPasswordFailure(self, match, tag):

        self.Authentication = False
        self.Error(['Password is wrong. Please enter correct Password.'])

    def SetPassword(self, value, qualifier):

        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def UpdateAirPressureStatus(self, value, qualifier):

        AirPressureStatusCmdString = 'extsensor all show\r'
        res = self.__UpdateHelper('AirPressureStatus', AirPressureStatusCmdString, value, qualifier)
        if res:

            values_list = re.findall(self.ProbeValuesRegEx, res)
            values_dict = {int(values_list[cnt][0]): values_list[cnt][1] for cnt in range(0, len(values_list))}

            try:    # Air Pressure Status (3)
                if 3 in values_dict:
                    value = round(float(values_dict[3]), 1)
                    self.WriteStatus('AirPressureStatus', value, None)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Air Pressure Status: Invalid/unexpected response'])

            try:    # Dew Point Status (4)
                if 4 in values_dict:
                    value = round(float(values_dict[4]), 1)
                    self.WriteStatus('DewPointStatus', value, None)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Dew Point Status: Invalid/unexpected response'])

            try:    # Dew Point Temperature Difference Status (5)
                if 5 in values_dict:
                    value = round(float(values_dict[5]), 1)
                    self.WriteStatus('DewPointTemperatureDifferenceStatus', value, None)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Dew Point Temperature Difference Status: Invalid/unexpected response'])

            try:    # Humidity Status (1)
                if 1 in values_dict:
                    value = round(float(values_dict[1]), 1)
                    self.WriteStatus('HumidityStatus', value, None)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Humidity Status: Invalid/unexpected response'])

            try:    # Temperature Status (0)
                if 0 in values_dict:
                    value = round(float(values_dict[0]), 1)
                    self.WriteStatus('TemperatureStatus', value, None)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Temperature Status: Invalid/unexpected response'])

    def UpdateDewPointStatus(self, value, qualifier):

        self.UpdateAirPressureStatus( None, qualifier)

    def UpdateDewPointTemperatureDifferenceStatus(self, value, qualifier):

        self.UpdateAirPressureStatus( None, qualifier)

    def UpdateHumidityStatus(self, value, qualifier):

        self.UpdateAirPressureStatus( None, qualifier)

    def SetPower(self, value, qualifier):

        PortStates = ['1', '2', '3', '4']

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        port_no = qualifier['Port']
        if port_no in PortStates and value in ValueStateValues:
            PowerCmdString = 'port {} state set {}\r'.format(port_no, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PortStates = ['1', '2', '3', '4']
        
        port_no = qualifier['Port']
        if port_no in PortStates:
            PowerCmdString = 'port all state 1 show\r'
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    result_list = re.findall(self.PowerListRegEx, res)
                    for result in result_list:
                        value = result[1].title()
                        qualifier = {'Port': result[0]}
                        self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Update Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def UpdatePowerActiveStatus(self, value, qualifier):

        PowerActiveStatusCmdString = 'linesensor all "0,1,2,3,21" show\r'
        res = self.__UpdateHelper('PowerActiveStatus', PowerActiveStatusCmdString, value, qualifier)
        if res:
            regex_result = re.search(self.ActivePowerRegEx, res)
            try:
                if regex_result.group(2) == 'kWh':
                    value = round(float(regex_result.group(1)), 3)
                else:
                    value = round(float(regex_result.group(1)) / 1000, 3)
                self.WriteStatus('TotalActiveEnergyStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Total Active Energy Status: Invalid/unexpected response'])
            try:
                value = round(float(regex_result.group(3)), 1)
                self.WriteStatus('PowerActiveStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Update Power Active Status: Invalid/unexpected response'])
            try:
                value = round(float(regex_result.group(4)), 1)
                self.WriteStatus('VoltageStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Voltage Status: Invalid/unexpected response'])
            try:
                value = round(float(regex_result.group(5)), 3)
                self.WriteStatus('CurrentStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Current Status: Invalid/unexpected response'])
            try:
                value = round(float(regex_result.group(6)), 3)
                self.WriteStatus('ResidualCurrentStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Residual Current Status: Invalid/unexpected response'])

    def UpdateTemperatureStatus(self, value, qualifier):

        self.UpdateAirPressureStatus(None, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERR' in response:
            self.Error(['Error occurred with command: {0}'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n>')
            if not res:
                self.Error(['No response received'])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authentication in ['Not Needed', True]:
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
                    
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n>')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authentication = 'Not Needed'

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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, deviceUsername=Credentials[0], devicePassword=Credentials[1])
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