from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:


    
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'nwk'
        self.devicePassword = 'nwk'        
        self.Models = {
            'Grafik 5000': self.lutr_13_1033_512,
            'Grafik 6000': self.lutr_13_1033_512,
            'Grafik 7000': self.lutr_13_1033_512,
            'OMX-CI-RS232': self.lutr_13_1033_512,
            'OMX-RS232': self.lutr_13_1033_512,
            'OMX-CI-NWK-E': self.lutr_13_1033_512,
            'LCP128': self.lutr_13_1033_128,
            'Softswitch128': self.lutr_13_1033_128,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FadetoLevel': {'Parameters':['Zone','Delay','Fade'], 'Status': {}},
            'FadetoLevelStatus': {'Parameters':['Zone'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
        }

        if 'Serial' not in self.ConnectionType:
            self.StartQuery = False
        else:
            self.StartQuery = True



                    


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'bad login'), self.__MatchPasswordFailure, None)

        self.expectedresp = re.compile('Error #([0-9]{1,3})\r\n')

    
    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchUsername(self, match, qualifier):

        self.SetUsername(None, None)
        
    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
            self.StartQuery = True
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, qualifier):

        self.SetPassword( None, None)
        
    def __MatchPasswordFailure(self, match, tag):

        self.StartQuery = False
        self.Error(['Login Credentials are wrong. Please enter correct Username and Password.'])





    def SetFadetoLevel(self, value, qualifier):

        DelayConstraints = {
            'Min' : 10,
            'Max' : 63000
        }

        FadeConstraints = {
            'Min' : 10,
            'Max' : 63000
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 127
        }

        Zone = int(qualifier['Zone'])
        Fade = int(qualifier['Fade']) * 10
        Delay = int(qualifier['Delay']) * 10

        if self.ZoneRange['Min'] <= Zone <= self.ZoneRange['Max']:
            if FadeConstraints['Min'] <= Fade <= FadeConstraints['Max'] and DelayConstraints['Min'] <= Delay <= DelayConstraints['Max']:
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    FadetoLevelCmdString = '~11h 7 {0:0X} {1:0X} {2:0X} {3:0X}\r'.format(value, Fade, Delay, Zone)
                    self.__SetHelper('FadetoLevel', FadetoLevelCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetFadetoLevel')
            else:
                self.Discard('Invalid Command for SetFadetoLevel')
        else:
            self.Discard('Invalid Command for SetFadetoLevel')
            
    def UpdateFadetoLevelStatus(self, value, qualifier):


        Zone = int(qualifier['Zone'])

        if self.ZoneRange['Min'] <= Zone <= self.ZoneRange['Max']:
            FadetoLevelStatusCmdString = '~11h 805 {0:0X}\r'.format(Zone)
            res = self.__UpdateHelper('FadetoLevelStatus', FadetoLevelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[4:-1],16)
                    self.WriteStatus('FadetoLevelStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Fade to Level Status: Invalid/unexpected response'])


    def SetPresetRecall(self, value, qualifier):

        if self.PresetRange['Min'] <= value <= self.PresetRange['Max']:
            PresetRecallCmdString = '~11h 12 {0:0X}\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')


    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
              '1': "232 string framing error",
              '2': "232 string buffer error",
              '4': "No response from the processor",
              '5': "No tilde (~) sent",
              '6': "No ~11h sent",
              '8': "232 string check is wrong when using ~11h",
              '31': "Network address illegally formatted. 4 octets required",
              '100': "Invalid Telnet login number",
              '101': "Invalid Telnet login",
              '102': "Login name exceeds 8 characters",
              '103': "Invalid number of arguments"
        }
        
        match = re.search(self.expectedresp,response)
        if match:
            errorString = '{0}'.format(DEVICE_ERROR_CODES[match.group(1)])
            self.Error([errorString])
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.StartQuery:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
                if not res:
                    self.Error(['{0}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Send('\r')
            self.Discard('Inappropriate Command')
            return ''

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.StartQuery:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
                
                return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Send('\r')
            self.Discard('Inappropriate Command ' + command)
            return ''

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.Send('\r')


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.StartQuery = False
        else:
            self.StartQuery = True
        

    def lutr_13_1033_512(self):
        self.ZoneRange = {
            'Min': 1,
            'Max': 512
        }

        self.PresetRange = {
            'Min': 0,
            'Max': 16000
        }


    def lutr_13_1033_128(self):
        self.ZoneRange = {
            'Min': 1,
            'Max': 128
        }

        self.PresetRange = {
            'Min': 0,
            'Max': 32
        }
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        Command = self.Commands[command]
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
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
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

