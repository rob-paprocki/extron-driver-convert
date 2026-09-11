from extronlib.system import Wait, ProgramLog
import urllib.error
import urllib.request
import base64
from json import loads, dumps

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DecoderPreset': { 'Status': {}},
            'Mode': { 'Status': {}},
            'Reboot': { 'Status': {}},
        }

        self.access_token = ''
        self.access_session = ''
        self._headers = {}

    def SetLogin(self, value, qualifier):

        temp_url = 'api/v1/user/authorize?username={}&password={}'.format(self.deviceUsername, self.devicePassword)
        url = '{}{}'.format(self.RootURL, temp_url)
        my_request = urllib.request.Request(url, data=None, method='POST')
        response = urllib.request.urlopen(my_request, timeout=10)
        if response:
            try:
                res = loads(response.read().decode())
                if res['result'] == 'ok':
                    self.access_session = res['data']['session']
                    self.access_token = res['data']['token']
                    self._headers['API-Session'] = '{}'.format(self.access_session)
                    self._headers['API-Token']   = '{}'.format(self.access_token)
            except:
                self.Error(['Login: Invalid/unexpected response'])
        else:
            self.Error(['Login Failed'])   

    def SetDecoderPreset(self, value, qualifier):

        ValueStateValues = {
            'Blank': '0', 
            '1': '1', 
            '2': '2', 
            '3': '3', 
            '4': '4', 
            '5': '5', 
            '6': '6', 
            '7': '7', 
            '8': '8', 
            '9': '9'
        }

        if self.access_session and self.access_token:
            if value in ValueStateValues:
                url = 'api/v1/decoder/current/set'
                data = dumps({"id": ValueStateValues[value]})
                self.__SetHelper('DecoderPreset', value, qualifier, url, data.encode())
            else:
                self.Discard('Invalid Command for SetDecoderPreset')
        else:
            self.SetLogin(None, None)

    def SetMode(self, value, qualifier):

        ValueStateValues = ('Encoder', 'Decoder')

        if self.access_session and self.access_token:
            if value in ValueStateValues:
                url = 'api/v1/mode/switch'
                data = dumps({"mode": value.lower()})
                self.__SetHelper('Mode', value, qualifier, url, data.encode())
            else:
                self.Discard('Invalid Command for SetMode')
        else:
            self.SetLogin( None, None)

    def UpdateMode(self, value, qualifier):

        ValueStateValues = {
            'encoder': 'Encoder', 
            'decoder': 'Decoder'
        }

        if self.access_session and self.access_token:
            url = 'api/v1/mode/get'
            res = self.__UpdateHelper('Mode', value, qualifier, url)
            if res:
                try:
                    value = ValueStateValues[res['data']['mode']]
                    self.WriteStatus('Mode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Mode: Invalid/unexpected response'])
        else:
            self.SetLogin( None, None)

    def SetReboot(self, value, qualifier):

        if self.access_session and self.access_token:
            url = 'api/v1/sys/reboot'
            self.__SetHelper('Reboot', value, qualifier, url)
        else:
            self.SetLogin( None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        self._headers['Content-Type'] = 'application/json'
        my_request = urllib.request.Request(url, data=data, headers=self._headers, method='POST')

        try:
            res = urllib.request.urlopen(my_request, timeout=5)
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            elif res.status == 401:
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                self.SetLogin(None, None)
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url)
        self._headers['Content-Type'] = 'application/json'
        my_request = urllib.request.Request(url, data=data, headers=self._headers)

        try:
            res = urllib.request.urlopen(my_request, timeout=5)
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            elif res.status == 401:
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                self.SetLogin(None, None)
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.access_token = ''
        self.access_session = ''

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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])