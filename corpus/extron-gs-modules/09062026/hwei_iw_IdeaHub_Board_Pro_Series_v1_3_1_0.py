import urllib.error
import urllib.request
import json
from extronlib.system import ProgramLog, GetUnverifiedContext


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername='api', devicePassword='Change_Me', SSLVerifyMode='On'):

        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.RootURL = 'https://{0}:{1}/'.format(self.IPAddress, self.DefaultPort)
        self._context = GetUnverifiedContext() if SSLVerifyMode == 'Off' else None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'MicMute': { 'Status': {}},
            'MicVolume': { 'Status': {}},
            'Power': { 'Status': {}},
            'Presentation': { 'Status': {}},
            'PresentationSource': { 'Status': {}},
            'SessionUpdate': { 'Status': {}},
            'SleepMode': { 'Status': {}},
            'TokenUpdate': { 'Status': {}},
            }
        
        self.SessionID = None
        self.acCSRFToken = None

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'WEB_CloseMicAPI', 
            'Off': 'WEB_OpenMicAPI'
        }
        
        if value in ValueStateValues:
            self.__SetHelper('MicMute', value, qualifier, url='action.cgi?ActionID={}'.format(ValueStateValues[value]), data={"acCSRFToken": self.acCSRFToken})
        else:
            self.Discard('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        MuteState = {
            0: 'On', 
            1: 'Off'
        }
        
        if not self.SessionID:
            self.SetSessionUpdate(None, None)
        elif not self.acCSRFToken:
            self.SetTokenUpdate(None, None)
        else:
            res = self.__UpdateHelper('MicMute', value, qualifier, url='action.cgi?ActionID=WEB_GetMailboxDataAPI', data={"acCSRFToken": self.acCSRFToken})
            if res:
                try:
                    if res["success"] == 1:
                        try:
                            self.WriteStatus('MicMute', MuteState[res["data"]["state"]["mic"]], qualifier)
                        except KeyError:
                            self.Error(['Mic Mute: Invalid/unexpected response'])
                        try:
                            self.WriteStatus('MicVolume', int(res["data"]["state"]["micValue"]), qualifier)
                        except (KeyError, ValueError):
                            self.Error(['Mic Volume: Invalid/unexpected response'])
                    else:
                        raise ValueError
                except (KeyError, ValueError):
                    self.SessionID = None
                    self.acCSRFToken = None
                    self.Error(['Mic Mute/Volume: Invalid/unexpected response'])
                    self.SetSessionUpdate(None, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off'    : 'WEB_RequestPowerDownAPI',
            'Restart': 'WEB_RequestRebootAPI'
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', value, qualifier, url='action.cgi?ActionID={}'.format(ValueStateValues[value]), data={"acCSRFToken": self.acCSRFToken})
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': 'WEB_StartSendAuxStreamAPI', 
            'Stop' : 'WEB_StopSendAuxStreamAPI'
        }
        
        if value in ValueStateValues:
            self.__SetHelper('Presentation', value, qualifier, url='action.cgi?ActionID={}'.format(ValueStateValues[value]), data={"acCSRFToken": self.acCSRFToken})
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdatePresentation(self, value, qualifier):

        ValueStateValues = {
            'auxOpen' : 'Start', 
            'auxClose': 'Stop'
        }

        res = self.__UpdateHelper('Presentation', value, qualifier, url='action.cgi?ActionID=WEB_IsSendAuxStreamAPI', data={"acCSRFToken": self.acCSRFToken})
        if res:
            try:
                value = ValueStateValues[res["data"]["isSendAux"]]
                self.WriteStatus('Presentation', value, qualifier)
            except KeyError:
                self.Error(['Presentation: Invalid/unexpected response'])

    def UpdatePresentationSource(self, value, qualifier):

        ValueStateValues = {
            'connect'  : 'Connected', 
            'unconnect': 'Not Connected'
        }
        res = self.__UpdateHelper('PresentationSource', value, qualifier, url='action.cgi?ActionID=WEB_IsConnectAuxSourceAPI', data={"acCSRFToken": self.acCSRFToken})
        if res:
            try:
                value = ValueStateValues[res["data"]["isSrcConnect"]]
                self.WriteStatus('PresentationSource', value, qualifier)
            except KeyError:
                self.Error(['Presentation Source: Invalid/unexpected response'])

    def SetSessionUpdate(self, value, qualifier):
        self.Debug = True
        
        res = self.__UpdateHelper('SessionUpdate', value, qualifier, url='action.cgi?ActionID=WEB_RequestSessionIDAPI')
        if res:
            try:
                if res["success"] == 1 and len(res["data"]["acSessionId"]) > 2:
                    self.SessionID = res["data"]["acSessionId"]
                    self.SetTokenUpdate(None, None)
                else:
                    raise ValueError
            except (KeyError, ValueError):
                self.SessionID = None
                self.Error(['Session Update: Invalid/unexpected response'])

    def SetSleepMode(self, value, qualifier):

        ValueStateValues = {
            'On' : 'StartTermSleepAPI', 
            'Off': 'SystemWakeUpAPI'
        }
        
        if value in ValueStateValues:
            self.__SetHelper('SleepMode', value, qualifier, url='action.cgi?ActionID=WEB_{}'.format(ValueStateValues[value]), data={"acCSRFToken": self.acCSRFToken})
        else:
            self.Discard('Invalid Command for SetSleepMode')

    def UpdateSleepMode(self, value, qualifier):

        ValueStateValues = {
            'sleep'  : 'On', 
            'unsleep': 'Off'
        }
        res = self.__UpdateHelper('SleepMode', value, qualifier, url='action.cgi?ActionID=WEB_IsSystemSleepAPI', data={"acCSRFToken": self.acCSRFToken})
        if res:
            try:
                value = ValueStateValues[res["data"]["isSystemSleep"]]
                self.WriteStatus('SleepMode', value, qualifier)
            except KeyError:
                self.Error(['Sleep Mode: Invalid/unexpected response'])

    def SetTokenUpdate(self, value, qualifier):
        self.Debug = True

        if not self.SessionID:
            self.SetSessionUpdate(None, None)
        else:
            res = self.__UpdateHelper('TokenUpdate', value, qualifier, url='action.cgi?ActionID=WEB_RequestCertificateAPI', data={"user": self.deviceUsername, "password": self.devicePassword})
            if res:
                try:
                    if res["success"] == 1:
                        self.acCSRFToken = res["data"]["acCSRFToken"]
                    else:
                        raise ValueError
                except (KeyError, ValueError):
                    self.acCSRFToken = None
                    self.Error(['Token Update: Invalid/unexpected response'])
                    self.SetSessionUpdate(None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return json.loads(response.read().decode().replace('\\', '').replace('}"', '}').replace('"{', '{'))

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        if self.acCSRFToken:
            url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
            if data is not None:
                data = json.dumps(data).encode()
            headers = {'Sessionid': self.SessionID, 'Content-Type': 'application/json'}

            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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
        else:
            self.Discard('Not Authenticated')

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.acCSRFToken or command in ['SessionUpdate', 'TokenUpdate']:
            if command not in ['SessionUpdate', 'TokenUpdate']:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

            url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
            if data is not None:
                data = json.dumps(data).encode()
            if not self.SessionID:
                headers = {'Content-Type': 'application/json'}
            else:
                headers = {'Sessionid': self.SessionID, 'Content-Type': 'application/json'}

            my_request = urllib.request.Request(url, data, headers=headers, method='POST')

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
        else:
            self.Discard('Not Authenticated')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetSessionUpdate(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.SessionID = None
        self.acCSRFToken = None

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
        port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.DefaultPort)
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername='api', devicePassword='Change_Me', Model=None, SSLVerifyMode='On'):
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