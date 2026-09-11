# Copyright 2026, Extron. All rights reserved.

from extronlib.system import ProgramLog, Wait, GetUnverifiedContext
import urllib.error
import urllib.request
import json
import time

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode):

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
            'MicMute': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.cookie_jar = urllib.request.HTTPCookieProcessor()
        self.Opener.add_handler(self.cookie_jar)
        self.x_xsrf_token = None
        self.virtual_disable = False
        self.lastLoginResponse = 0

    def SetLogin(self, value, qualifier):

        self.cookie_jar.cookiejar.clear()
        self.x_xsrf_token = None
    
        if self.virtual_disable:
            self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
            return
        url = '{}rest/session'.format(self.RootURL)
        headers = {
            'Content-Type': 'application/json'
        }
        data = json.dumps({'user': self.deviceUsername, 'password': self.devicePassword}, separators=(',', ':')).encode(encoding='iso-8859-1')

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format('Login', err.code, err.reason)])

            if err.code == 403:
                res = json.loads(err.read().decode())
                if res['reason'] == 'SessionInvalidUserNamePassword':
                    self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
                    self.virtual_disable = True

                elif res['reason'] == 'SessionMaxActiveSessionsReached':
                    self.Error(['Login failed: Max active sessions reached.'])
                
                else:
                    self.Error(['Login failed: {}'.format(res['reason'])])

        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format('Login', err.reason)])
        except Exception as err:
            pass
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format('Login', res.status, res.msg)])
            else:

                try:
                    res = json.loads(res.read().decode())

                    if res['success'] == True:
                        for cookie in self.cookie_jar.cookiejar:
                            if cookie.name.lower() == 'xsrf-token':
                                self.x_xsrf_token = cookie.value
                                break
                        self.lastLoginResponse = 0
                        self.Error(['Login success.'])
                            
                        return
                    else:
                        self.Error(['Login failed.'])
                except:
                    self.Error(['Login: Invalid/unexpected response'])
        self.lastLoginResponse = time.monotonic()

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if value in ValueStateValues:
            MicMuteCmdString = 'audio/muted'
            data = json.dumps(ValueStateValues[value]).encode()

            self.__SetHelper('MicMute', value, qualifier, url=MicMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }

        MicMuteCmdString = 'audio/muted'
        res = self.__UpdateHelper('MicMute', value, qualifier, url=MicMuteCmdString)
        if res:
            try:
                self.WriteStatus('MicMute', ValueStateValues[json.loads(res)], qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Mic Mute: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'video/local/mute'
            data=json.dumps({'mute': ValueStateValues[value]}).encode()

            self.__SetHelper('VideoMute', value, qualifier, url=VideoMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }

        VideoMuteCmdString = 'video/local/mute'
        res = self.__UpdateHelper('VideoMute', value, qualifier, url=VideoMuteCmdString)
        if res:
            try:
                value = ValueStateValues[json.loads(res)['result']]
                self.WriteStatus('VideoMute', value, qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'audio/volume'
            data = json.dumps(value).encode()
            
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'audio/volume'
        res = self.__UpdateHelper('Volume', value, qualifier, url=VolumeCmdString)
        if res:
            try:
                value = int(json.loads(res))
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except (json.decoder.JSONDecodeError, ValueError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None, method=None):

        self.Debug = True

        if self.virtual_disable:
            self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the module.'])
            return
        if time.monotonic() - self.lastLoginResponse < 1:
            self.Error(['Login: Device Is Busy'])
            return
        
        url = '{}rest/{}'.format(self.RootURL, url)
        headers = {}

        if not method:
            method = 'POST' if data else 'GET'
        
        if method == 'POST' and data is not None:
            headers['Content-Type'] = 'application/json'

        if self.x_xsrf_token and method in {'POST', 'PUT', 'DELETE'}:
            headers['X-XSRF-Token'] = self.x_xsrf_token

        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])

            if err.code == 403:
                self.SetLogin( None, None)

            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 201, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None, method='GET'):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.virtual_disable:
            self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the module.'])
            return
        if time.monotonic() - self.lastLoginResponse < 1:
            self.Error(['Login: Device Is Busy'])
            return
        
        url = '{}rest/{}'.format(self.RootURL, url)
        headers = {}
        
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])

            if err.code == 403:
                self.SetLogin( None, None)

            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
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
        
        self.lastLoginResponse = 0

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