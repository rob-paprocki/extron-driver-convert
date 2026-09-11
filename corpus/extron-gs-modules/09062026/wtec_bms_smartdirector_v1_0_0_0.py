# Copyright 2026, Extron. All rights reserved.

from extronlib.system import ProgramLog, Wait, GetUnverifiedContext
import base64
import urllib.error
import urllib.request
import base64
import json

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
            'Brightness': {'Parameters': ['Location ID'], 'Status': {}},
            'Name': { 'Status': {}},
            'SceneRecallCommand': {'Parameters': ['Location ID'], 'Status': {}},
            'SceneStatus': {'Parameters': ['Location ID'], 'Status': {}}
        }

        if self.deviceUsername is not None and self.devicePassword is not None:
            self.base64Auth = 'Basic ' + base64.b64encode(self.deviceUsername.encode() + b':' + self.devicePassword.encode()).decode()
        else:
            self.Error(['Missing Username and Password.'])

    def SetBrightness(self, value, qualifier):

        if 0 <= qualifier['Location ID'] and 0 <= value <= 100:
            BrightnessCmdString = 'uApi'
            data = {
                "protocolVersion" : "1",
                "schemaVersion" : "1.4.0",
                "requestType" : "set",
                "requestData" : {
                "location" : [
                    {
                        "id" : qualifier['Location ID'],
                        "wallSwitch": {
                            "lowLevelControl": {
                                "brightness": value,
                                "activated": 999999999999
                            }
                        }
                    }
                    ]
                }
            }

            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        if 0 <= qualifier['Location ID']:
            BrightnessCmdString = 'rApi/location/{}/wallSwitch/lowLevelControl'.format(qualifier['Location ID'])
            res = self.__UpdateHelper('Brightness', value, qualifier, url=BrightnessCmdString)
            if res:
                try:
                    value = int(res['brightness'])
                    self.WriteStatus('Brightness', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Brightness: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def UpdateName(self, value, qualifier):

        NameCmdString = 'rApi/name'
        res = self.__UpdateHelper('Name', value, qualifier, url=NameCmdString)
        if res is not None: # None check in case name returned is blank
            try:
                value = res.strip()
                self.WriteStatus('Name', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Name: Invalid/unexpected response'])

    def SetSceneRecallCommand(self, value, qualifier):

        scene = value

        if 0 <= qualifier['Location ID'] and scene is not None:
            SceneRecallCommandCmdString = 'rApi/location/{}/sceneControl/activeSceneName'.format(qualifier['Location ID'])
            self.__SetHelper('SceneRecallCommand', value, qualifier, url=SceneRecallCommandCmdString, data=scene)
        else:
            self.Discard('Invalid Command for SetSceneRecallCommand')
            
    def UpdateSceneStatus(self, value, qualifier):

        if 0 <= qualifier['Location ID']:
            SceneStatusCmdString = 'rApi/location/{}/sceneControl/activeSceneName'.format(qualifier['Location ID'])
            res = self.__UpdateHelper('SceneStatus', value, qualifier, url=SceneStatusCmdString)
            if res is not None: # None check in case scene returned is blank for no active scene
                try:
                    value = res.strip()
                    self.WriteStatus('SceneStatus', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Scene Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSceneStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except:
            self.Error(['{}: Invalid/unexpected respnse'.format(sourceCmdName)])

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Authorization': self.base64Auth,
        }

        if data is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST' if command == 'Brightness' else 'PUT')

        try:
            res = self.Opener.open(my_request, timeout=1)
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

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Authorization': self.base64Auth
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)
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