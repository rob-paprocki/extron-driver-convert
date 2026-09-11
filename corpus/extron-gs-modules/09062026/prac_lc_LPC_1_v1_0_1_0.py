from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request
import json

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
            'FirmwareVersion': { 'Status': {}},
            'Scene': {'Parameters': ['Scene'], 'Status': {}},
            'Timeline': {'Parameters': ['Timeline'], 'Status': {}},
            'Token': { 'Status': {}},
            'Trigger': { 'Status': {}},
        }

        self.token = ''

    def SetLogin(self, value, qualifier):

        res = {}

        data = json.dumps({
            'user': self.deviceUsername,
            'password': self.devicePassword
        }).encode()

        url = '{}{}'.format(self.RootURL, 'token')
        headers = {'Content-Type': 'applcation/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format('Login', err.code, err.reason)])
            res = {}
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format('Login', err.reason)])
            res = {}
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = {}
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format('Login', res.status, res.msg)])
                res = {}
            else:
                res = self.__CheckResponseForErrors('Login', res)

        if res:
            try:
                self.token = res['access_token']
            except KeyError:
                self.Error(['Login: Invalid/unexpected response'])

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'api/system'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=FirmwareVersionCmdString)
        if res:
            try:
                value = res['firmware_version']
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (KeyError, TypeError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetScene(self, value, qualifier):

        scene = qualifier['Scene']

        ValueStateValues = [
            'Start',
            'Release',
            'Toggle'
        ]

        if 1 <= scene and value in ValueStateValues:
            data = {
                'action': value.lower(),
                'num': scene
            }

            SceneCmdString = 'api/scene'
            self.__SetHelper('Scene', value, qualifier, url=SceneCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetScene')

    def SetTimeline(self, value, qualifier):

        timeline = qualifier['Timeline']

        ValueStateValues = [
            'Start',
            'Release',
            'Toggle',
            'Pause',
            'Resume'
        ]

        if 1 <= timeline and value in ValueStateValues:
            data = {
                'action': value.lower(),
                'num': timeline
            }

            TimelineCmdString = 'api/timeline'
            self.__SetHelper('Timeline', value, qualifier, url=TimelineCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetTimeline')

    def UpdateToken(self, value, qualifier):

        self.SetLogin(None, None)

    def SetTrigger(self, value, qualifier):

        if 1 <= value:
            data = {
                'num' : value
            }

            TriggerCmdString = 'api/trigger'
            self.__SetHelper('Trigger', value, qualifier, url=TriggerCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetTrigger')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except json.decoder.JSONDecodeError:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
            return {}

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Content-Type': 'application/json'
        }

        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''

            if err.code == 401:
                self.SetLogin(None, None)
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

        url = '{}{}'.format(self.RootURL, url)
        headers = {}

        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''

            if err.code == 401:
                self.SetLogin(None, None)
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