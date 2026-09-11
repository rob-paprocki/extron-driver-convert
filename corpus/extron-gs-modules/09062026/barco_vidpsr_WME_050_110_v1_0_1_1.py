from extronlib.system import Wait, ProgramLog, GetUnverifiedContext
import base64
import urllib.error
import urllib.request
import json
import time
from extronlib import Version

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, SSLVerifyMode='On'):

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
        self._SecurityKey = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Brightness': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': {'Parameters': ['Name'], 'Status': {}}
        }

        self.session_id = None # actual token used in http requests
        self.session_ex = None # session expiration in seconds
        self.session_ts = None # time.monotonic timestamp for when token was generated

    @property
    def SecurityKey(self):
        return self._SecurityKey

    @SecurityKey.setter
    def SecurityKey(self, value):
        self._SecurityKey = value

    def generate_token(self):
        command = 'GetToken'

        self.session_id = None
        self.session_ex = None
        self.session_ts = None

        url = '{}api/v1/auth/key'.format(self.RootURL)

        headers = {
            'Content-Type': 'application/json'
        }

        data = json.dumps({
            'type': 'REST',
            'key':  self._SecurityKey
        }).encode()

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            pass
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
            else:
                if res.headers.get('Set-Cookie', None) is not None:
                    try:
                        self.session_ex = json.loads(res.read().decode())['expiresIn']
                        self.session_id = res.headers['Set-Cookie']
                        self.session_ts = time.monotonic()

                        return
                    except:
                        pass
        
        self.Error(['Get Token: Failed to generate security token.'])
    
    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            BrightnessCmdString = 'api/v1/wall/brightness'
            data = {
                'brightness': value
            }

            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'api/v1/wall/brightness'
        res = self.__UpdateHelper('Brightness', value, qualifier, url=BrightnessCmdString)
        if res:
            try:
                value = res['brightness']
                if 0 <= value <= 100:
                    self.WriteStatus('Brightness', value, qualifier)
                else:
                    self.Error(['Brightness: Invalid/unexpected response'])
            except (ValueError, KeyError, TypeError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Idle',
            'Standby'
        ]

        if value in ValueStateValues:
            PowerCmdString = 'api/v1/wall/power'
            data = {
                'power': value.lower()
            }

            self.__SetHelper('Power', value, qualifier, url=PowerCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'on':       'On',
            'idle':     'Idle',
            'standby':  'Standby'
        }

        PowerCmdString = 'api/v1/wall/power'
        res = self.__UpdateHelper('Power', value, qualifier, url=PowerCmdString)
        if res:
            try:
                value = ValueStateValues[res['power']]
                self.WriteStatus('Power', value, qualifier)
            except (ValueError, KeyError, TypeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        name = qualifier['Name']

        if 1 <= len(name):
            PresetRecallCmdString = 'api/v1/wall/preset'
            data = {
                'name': name
            }

            self.__SetHelper('PresetRecall', value, qualifier, url=PresetRecallCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = json.loads(response.read().decode())

            if 'error' in response:
                self.Error(['An error occurred: {}: {}: {}'.format(sourceCmdName,
                                                                response['error'].get('code', 'Unknown code'),
                                                                response['error'].get('message', 'Unknown error.'))])

            return response
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        if self.session_id is not None and self.session_ts + self.session_ex - time.monotonic() < 60:
            print('Generating new token.')
            self.generate_token()

        if self.session_id:
            url = '{}{}'.format(self.RootURL, url)
            headers = {
                'Content-Type': 'application/json',
                'Cookie':       self.session_id
            }
            data = json.dumps(data).encode()

            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

            try:
                res = self.Opener.open(my_request, timeout=10)
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])

                if err.code == 401:
                    self.Error(['Invalid token. Generating new token.'])
                    self.generate_token()
                    
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
        else:   
            self.Error(['Token not generated.'])
            self.generate_token()

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.session_id is not None and self.session_ts + self.session_ex - time.monotonic() < 60:
            print('Generating new token.')
            self.generate_token()

        if self.session_id:

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            url = '{}{}'.format(self.RootURL, url)
            headers = {
                'Cookie': self.session_id
            }

            my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

            try:
                res = self.Opener.open(my_request, timeout=10)
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])

                if err.code == 401:
                    self.Error(['Invalid token. Generating new token.'])
                    self.generate_token()

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
        else:   
            self.Error(['Token not generated.'])
            self.generate_token()

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')

        self.connectionFlag = False
        
        self.session_id = None
        self.session_ex = None
        self.session_ts = None

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