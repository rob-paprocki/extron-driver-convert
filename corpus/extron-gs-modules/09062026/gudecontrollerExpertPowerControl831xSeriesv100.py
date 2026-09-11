from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, findall, match, search

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
        self.deviceUsername = None
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActivePowerStatus': { 'Status': {}},
            'AirPressureStatus': {'Parameters':['Sensor'], 'Status': {}},
            'CurrentStatus': { 'Status': {}},
            'DewPointStatus': {'Parameters':['Sensor'], 'Status': {}},
            'DewPointTemperatureDifferenceStatus': {'Parameters':['Sensor'], 'Status': {}},
            'HumidityStatus': {'Parameters':['Sensor'], 'Status': {}},
            'OvervoltageProtectionStatus': { 'Status': {}},
            'Power': {'Parameters':['Port'], 'Status': {}},
            'ResidualCurrentStatus': { 'Status': {}},
            'TemperatureStatus': {'Parameters':['Sensor'], 'Status': {}},
            'TotalActiveEnergyStatus': { 'Status': {}},
            'VoltageStatus': { 'Status': {}},
        }

        self.Authentication = 'Not Needed'  # In case if Authentication is disabled from console
        
        ap_regex_str = r'L=1,L=".*?",OVP=([01]),0="(\d+?\.?\d*?)Wh",1="(\d+?\.?\d*?)W",2="(\d+?\.?\d*?)V",' \
                       r'3="(\d+?\.?\d*?)A",21="(\d+?\.?\d*?)A"\r\n>'
        self.ActivePowerRegEx = compile(ap_regex_str)
        self.PowerListRegEx = compile(r'P([1-8])=(ON|OFF)')
        self.ProbeNumberRegEx = compile(r'E=([12])')
        self.ProbeValuesRegEx = compile(r'([01345])="(\d*(?:\.\d+)?).+?"')

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\r\nConsole login: '), self.__MatchUsername, None)
            self.AddMatchString(compile(b'\r\nPassword: '), self.__MatchPassword, None)
            self.AddMatchString(compile(b'\r\nLogin accepted.\r\n>'), self.__MatchPasswordSuccessful, None)
            self.AddMatchString(compile(b'\r\nLogin failed.\r\n>'), self.__MatchPasswordFailure, None)

    def __MatchUsername(self, match, tag):

        self.SetUsername( None, None)
        self.Authentication = False  # Device asked for login means Authentication is enabled from Console

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

    def UpdateActivePowerStatus(self, value, qualifier):

        OvervoltageProtectionStateValues = {
            '0': 'Not OK',
            '1': 'OK',
        }

        ActivePowerStatusCmdString = 'linesensor all "0,1,2,3,21" show\r'
        res = self.__UpdateHelper('ActivePowerStatus', ActivePowerStatusCmdString, value, qualifier)
        if res:
            regex_result = match(self.ActivePowerRegEx, res)
            try:
                value = OvervoltageProtectionStateValues[regex_result.group(1)]
                self.WriteStatus('OvervoltageProtectionStatus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Overvoltage Protection Status: Invalid/unexpected response'])
            try:
                value = round(float(regex_result.group(2)) / 1000, 3)  # Converting Wh to kWh, see Web page
                self.WriteStatus('TotalActiveEnergyStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Total Active Energy Status: Invalid/unexpected response'])
            try:
                value = round(float(regex_result.group(3)), 1)
                self.WriteStatus('ActivePowerStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Active Power Status: Invalid/unexpected response'])
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

    def UpdateAirPressureStatus(self, value, qualifier):

        if 1 <= int(qualifier['Sensor']) <= 2:
            AirPressureStatusCmdString = 'extsensor all show\r'
            res = self.__UpdateHelper('AirPressureStatus', AirPressureStatusCmdString, value, qualifier)
            if res:
                result_list = list(filter(None, res[:-1].split('\r\n')))

                values_dict = {}
                for result in result_list:
                    probe_num = int(match(self.ProbeNumberRegEx, result).group(1))
                    values_list = findall(self.ProbeValuesRegEx, result)

                    values_dict[probe_num] = \
                        {int(values_list[cnt][0]): values_list[cnt][1] for cnt in range(0, len(values_list))}
                probe_num = list(values_dict)[0]
                qualifier = {'Sensor': str(probe_num)}
                qualifier1 = {'Sensor': '1'}
                qualifier2 = {'Sensor': '2'}
                try:
                    if len(values_dict) < 2:            # Only one result
                        if 3 in values_dict[probe_num]:
                            value = round(float(values_dict[probe_num][3]), 1)
                            self.WriteStatus('AirPressureStatus', value, qualifier)
                    else:                               # Two results
                        if 3 in values_dict[1]:
                            value1 = round(float(values_dict[1][3]), 1)
                            self.WriteStatus('AirPressureStatus', value1, qualifier1)
                        if 3 in values_dict[2]:
                            value2 = round(float(values_dict[2][3]), 1)
                            self.WriteStatus('AirPressureStatus', value2, qualifier2)
                except (ValueError, IndexError):
                    self.Error(['Air Pressure Status: Invalid/unexpected response'])
                try:
                    if len(values_dict) < 2:             # Only one result
                        if 4 in values_dict[probe_num]:
                            value = round(float(values_dict[probe_num][4]), 1)
                            self.WriteStatus('DewPointStatus', value, qualifier)
                    else:                               # Two results
                        if 4 in values_dict[1]:
                            value1 = round(float(values_dict[1][4]), 1)
                            self.WriteStatus('DewPointStatus', value1, qualifier1)
                        if 4 in values_dict[2]:
                            value2 = round(float(values_dict[2][4]), 1)
                            self.WriteStatus('DewPointStatus', value2, qualifier2)
                except (ValueError, IndexError):
                    self.Error(['Dew Point Status: Invalid/unexpected response'])
                try:
                    if len(values_dict) < 2:             # Only one result
                        if 5 in values_dict[probe_num]:
                            value = round(float(values_dict[probe_num][5]), 1)
                            self.WriteStatus('DewPointTemperatureDifferenceStatus', value, qualifier)
                    else:  # Two results
                        if 5 in values_dict[1]:
                            value1 = round(float(values_dict[1][5]), 1)
                            self.WriteStatus('DewPointTemperatureDifferenceStatus', value1, qualifier1)
                        if 5 in values_dict[2]:
                            value2 = round(float(values_dict[2][5]), 1)
                            self.WriteStatus('DewPointTemperatureDifferenceStatus', value2, qualifier2)
                except (ValueError, IndexError):
                    self.Error(['Dew Point Temperature Difference Status: Invalid/unexpected response'])
                try:
                    if len(values_dict) < 2:            # Only one result
                        if 1 in values_dict[probe_num]:
                            value = round(float(values_dict[probe_num][1]), 1)
                            self.WriteStatus('HumidityStatus', value, qualifier)
                    else:                               # Two results
                        if 1 in values_dict[1]:
                            value1 = round(float(values_dict[1][1]), 1)
                            self.WriteStatus('HumidityStatus', value1, qualifier1)
                        if 1 in values_dict[2]:
                            value2 = round(float(values_dict[2][1]), 1)
                            self.WriteStatus('HumidityStatus', value2, qualifier2)
                except (ValueError, IndexError):
                    self.Error(['Humidity Status: Invalid/unexpected response'])
                try:
                    if len(values_dict) < 2:            # Only one result
                        if 0 in values_dict[probe_num]:
                            value = round(float(values_dict[probe_num][0]), 1)
                            self.WriteStatus('TemperatureStatus', value, qualifier)
                    else:                               # Two results
                        if 0 in values_dict[1]:
                            value1 = round(float(values_dict[1][0]), 1)
                            self.WriteStatus('TemperatureStatus', value1, qualifier1)
                        if 0 in values_dict[2]:
                            value2 = round(float(values_dict[2][0]), 1)
                            self.WriteStatus('TemperatureStatus', value2, qualifier2)
                except (ValueError, IndexError):
                    self.Error(['Temperature Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAirPressureStatus')

    def UpdateDewPointStatus(self, value, qualifier):

        if 1 <= int(qualifier['Sensor']) <= 2:
            self.UpdateAirPressureStatus( None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDewPointStatus')

    def UpdateDewPointTemperatureDifferenceStatus(self, value, qualifier):

        if 1 <= int(qualifier['Sensor']) <= 2:
            self.UpdateAirPressureStatus( None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDewPointTemperatureDifferenceStatus')

    def UpdateHumidityStatus(self, value, qualifier):

        if 1 <= int(qualifier['Sensor']) <= 2:
            self.UpdateAirPressureStatus( None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHumidityStatus')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Port']) <= 8 and value in ValueStateValues:
            PowerCmdString = 'port {} state set {}\r'.format(qualifier['Port'], ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= 8:
            PowerCmdString = 'port all state 1 show\r'
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    result_list = findall(self.PowerListRegEx, res)
                    for result in result_list:
                        value = result[1].title()
                        qualifier = {'Port': result[0]}
                        self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def UpdateTemperatureStatus(self, value, qualifier):

        if 1 <= int(qualifier['Sensor']) <= 2:
            self.UpdateAirPressureStatus( None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperatureStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and response[0:3] == 'ERR':
            self.Error(['{0}: {1}'.format(sourceCmdName, response[:-3])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Authentication in ['Not Needed', True]:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n>')
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Invalid Command')

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

        self.Authentication = 'Not Needed'  # In case if Authentication is disabled from console
        
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
                result = search(regexString, self.__receiveBuffer)
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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