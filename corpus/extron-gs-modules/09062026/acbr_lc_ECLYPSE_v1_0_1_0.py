from extronlib.system import Wait, ProgramLog, GetUnverifiedContext
import urllib.error
import urllib.request
import base64
import json
from extronlib import Version

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
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = '1'
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Dimmer': {'Parameters': ['Instance ID'], 'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if int(value) < 0:
            self.Error(['Invalid Device ID Parameter.'])
        else:
            self._DeviceID = int(value)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'api/rest/v1/protocols/bacnet/local/objects/device/{}/properties/system-status'.format(self._DeviceID)
        res = self.__UpdateHelper('DeviceStatus', value, qualifier, DeviceStatusCmdString)
        if res:
            try:
                value = res['value']
                self.WriteStatus('DeviceStatus', value, qualifier)
            except KeyError:
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetDimmer(self, value, qualifier):

        iid = qualifier['Instance ID']

        if iid.isnumeric() and 0 <= value <= 100:
            DimmerCmdString = 'api/rest/v1/protocols/bacnet/local/objects/analog-value/{iid}/properties/presentValue'.format(iid=int(iid))
            data = json.dumps({
                    'value': '{:.1f}'.format(value)
                }).encode(encoding='iso-8859-1')

            self.__SetHelper('Dimmer', value, qualifier, DimmerCmdString, data)
        else:
            self.Discard('Invalid Command for SetDimmer')

    def UpdateDimmer(self, value, qualifier):

        iid = qualifier['Instance ID']

        if iid.isnumeric():
            DimmerCmdString = 'api/rest/v1/protocols/bacnet/local/objects/analog-value/{iid}/properties/presentValue'.format(iid=int(iid))
            res = self.__UpdateHelper('Dimmer', value, qualifier, DimmerCmdString)
            if res:
                try:
                    value = int(float(res['value']))

                    if 0 <= value <= 100:
                        self.WriteStatus('Dimmer', value, qualifier)
                except (KeyError, ValueError):
                    self.Error(['Dimmer: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDimmer')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except json.decoder.JSONDecodeError:
            return {}

    def __SetHelper(self, command, value, qualifier, url, data=None):

        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {
            'Accept'        : 'application/json',
            'Content-Type'  : 'application/json',
            'Authorization' : self.authentication
        }

        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(req, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
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

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL, url)

        headers = {
            'Accept'        : 'application/json',
            'Content-Type'  : 'application/json',
            'Authorization' : self.authentication
        }

        req = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(req, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
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