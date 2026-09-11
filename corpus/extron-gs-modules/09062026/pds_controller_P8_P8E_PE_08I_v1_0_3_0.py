from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import json


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'OutletPower': {'Parameters': ['Outlet Number'], 'Status': {}},
            }

        self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFF\xFD\x18'), self.__MatchPing1, None)
            self.AddMatchString(re.compile(b'\xFF\xFD\x01'), self.__MatchPing2, None)
            self.AddMatchString(re.compile(b'login as: '), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'password: '), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Welcome to Pakedge PDU.\r'), self.__MatchLoginSuccess, None)
            self.AddMatchString(re.compile(b'Invalid login, Access denied\r'), self.__MatchLoginFailed, None)
            self.AddMatchString(re.compile(b'show device-info({.*?})\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'show outlet-status -o ([1-8])({.*?})\r\n'), self.__MatchOutletPower, None)
            self.AddMatchString(re.compile(b'{"status":"error", "msg":"(.*?)"}\r\n'), self.__MatchError, None)

    def SetPong1(self, match, tag):

        self.Send(b'\xFF\xFC\x18')

    def __MatchPing1(self, match, tag):

        self.SetPong1(None, None)

    def SetPong2(self, match, tag):

        self.Send(b'\xFF\xFC\x01')

    def __MatchPing2(self, match, tag):

        self.SetPong2(None, None)

    def __MatchUsername(self, match, tag):

        self.SetUsername(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):

        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLoginFailed(self, match, tag):
        self.Authenticated = False

    def __MatchLoginSuccess(self, match, tag):
        self.Authenticated = True

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'show device-info\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = json.loads(match.group(1).decode())
        if value['status'] == 'success':
            self.WriteStatus('FirmwareVersion', value['response']['firmware_version'], None)
        else:
            ErrorString = 'Firmware Version: Error occurred. Error Message: {}\r\n'.format(value['msg'])
            self.Error([ErrorString])

    def SetOutletPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }
        OutletPowerCmdString = None
        if int(qualifier['Outlet Number']) in range(1, 9):
            outlet = qualifier['Outlet Number']
            if value != 'Cycle':
                OutletPowerCmdString = 'set outlet-power -o {0} -v {1}\r'.format(outlet, ValueStateValues[value])
            else:
                OutletPowerCmdString = 'power-cycle -o {0}\r'.format(outlet)
            if OutletPowerCmdString:
                self.__SetHelper('OutletPower', OutletPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutletPower')

    def UpdateOutletPower(self, value, qualifier):

        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }
        if int(qualifier['Outlet Number']) in range(1,9):
            outlet = qualifier['Outlet Number']           
            OutletPowerCmdString = 'show outlet-status -o {0}\r'.format(outlet) 
            self.__UpdateHelper('OutletPower', OutletPowerCmdString, value, qualifier)        
        else:
            self.Discard('Invalid Command for UpdateOutletPower')

    def __MatchOutletPower(self, match, tag):

        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off', 
        }

        outlet = match.group(1).decode()
        value = json.loads(match.group(2).decode())
        if value['status'] == 'success':
            self.WriteStatus('OutletPower', ValueStateValues[value['response']['status']], {'Outlet Number': outlet})
        elif value['status'] == 'error':
            ErrorString = 'Outlet Power #{}: Error occurred. Error Message: {}\r\n'.format(outlet, value['msg'])
            self.Error([ErrorString])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command' + command)
        elif self.Authenticated:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command {}.\r\nDevice is not logged in properly.'.format(command))

    def __MatchError(self, match, tag):

        value = match.group(1).decode()
        self.Error(['Error occurred: {}'.format(value)])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = False

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