from extronlib.system import ProgramLog, Wait, GetUnverifiedContext
import urllib.error
import urllib.request
import json
import base64

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

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
            'PoEConfiguration': {'Parameters':['Port','Power Limit Mode','Classification','Current Power','Power Limit','Status'], 'Status': {}},
            'PoEConfigurationStatus': {'Parameters':['Port'], 'Status': {}}
        }

        if self.deviceUsername and self.devicePassword:
            self.base64Auth = base64.b64encode(self.deviceUsername.encode() + b':' + self.devicePassword.encode()).decode()
        else:
            self.base64Auth = None
            self.Error(['Error: Missing Username and Password.'])

        self.poePortConfig = {}

    def SetPoEConfiguration(self, value, qualifier):

        PowerLimitModeStates = {
            'Invalid'   : 0,
            'DOT3AF'    : 1,
            'User'      : 2,
            'None'      : 3,
            'Count'     : 4
        }

        ClassificationStates = {
            'Invalid'   : 0,
            'Class 0'   : 1,
            'Class 1'   : 2,
            'Class 2'   : 3,
            'Class 3'   : 4
        }

        StatusStates = {
            'Invalid'           : -1,
            'Disabled'          : 0,
            'Searching'         : 1,
            'Delivering Power'  : 2,
            'Test'              : 3,
            'Fault'             : 4,
            'Other Fault'       : 5,
            'Requesting Power'  : 6,
            'Overload'          : 7
        }

        ValueStateValues = {
            'On'  : True,
            'Off' : False
        }

        if 1 <= int(qualifier['Port']) <= 96 and qualifier['Power Limit Mode'] in PowerLimitModeStates and qualifier['Classification'] in ClassificationStates and 0 <= qualifier['Current Power'] <= 30000 and 0 <= qualifier['Power Limit'] <= 30000 and qualifier['Status'] in StatusStates and value in ValueStateValues:
            PoEConfigurationCmdString = 'api/v1/swcfg_poe?portid={}'.format(qualifier['Port'])
            data = {
                "poePortConfig" : {
                    "portid" : int(qualifier['Port']),
                    "enable" : ValueStateValues[value],
                    "powerLimitMode" : PowerLimitModeStates[qualifier['Power Limit Mode']],
                    "classification" : ClassificationStates[qualifier['Classification']],
                    "currentPower" : qualifier['Current Power'],
                    "powerLimit" : qualifier['Power Limit'],
                    "status" : StatusStates[qualifier['Status']],
                    "reset" : False
                }
            }

            self.__SetHelper('PoEConfiguration', value, qualifier, url=PoEConfigurationCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetPoEConfiguration')

    def UpdatePoEConfigurationStatus(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= 96:
            PoEConfigurationStatusCmdString = 'api/v1/swcfg_poe?portid=ALL'
            res = self.__UpdateHelper('PoEConfigurationStatus', value, qualifier, url=PoEConfigurationStatusCmdString)
            if res:
                try:
                    ValueStateValues = {
                        True  : 'On',
                        False : 'Off'
                    }

                    poePort = res['poePortConfig']
                    for entry in poePort:
                        self.WriteStatus('PoEConfigurationStatus', ValueStateValues[entry['enable']], {'Port' : str(entry['portid'])})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['PoE Configuration Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePoEConfigurationStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = json.loads(response.read().decode('utf-8', 'ignore'))
            if response['resp']['status'] != 'success':
                self.Error(['Error: {}'.format(response['resp']['respMsg'])])
                response = ''
            return response
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {
            'Content-Type' : 'application/json',
            'Accept' : 'application/json',
            'Authorization' : 'Basic {}'.format(self.base64Auth)
        }

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
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

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {
            'Content-Type' : 'application/json',
            'Accept' : 'application/json',
            'Authorization' : 'Basic {}'.format(self.base64Auth)
        }

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
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

        self.poePortConfig = {}
        
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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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