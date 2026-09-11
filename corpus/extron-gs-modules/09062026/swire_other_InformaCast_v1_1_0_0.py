from extronlib.system import GetUnverifiedContext
import re
import json
import base64
import urllib.error
import urllib.request
from collections import OrderedDict


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.port = port

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        if self.port == 443:  # HTTPS
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else:  # HTTP
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AllNotifications': {'Status': {}},
            'BellSchedule': {'Parameters': ['Bell Schedule ID', 'Ring List ID', 'Start Date', 'End Date'], 'Status': {}},
            'Notifications': {'Parameters': ['Message Template ID'], 'Status': {}},
            'SendNotification': {'Parameters': ['Message Template ID', 'Subject'], 'Status': {}},
        }

        self.messageTemplateIds = []
        self.messageTemplateRegex = re.compile('\"messageTemplateId\": \"([a-f0-9\-]+)\"')
        

    @property
    def UserToken(self):
        return self._UserToken

    @UserToken.setter
    def UserToken(self, value):
        self._UserToken = value
        self.UpdateLogin()

    def UpdateLogin(self):
        res = self.__UpdateHelper('Login', None, None, url='session')
        if 'unauthorized' not in res:
            response = self.__UpdateHelper('MessageTemplateId', None, None, url='message-templates')
            if response:
                try:
                    self.messageTemplateIds = re.findall('\"id\": \"([a-f0-9\-]+)\","notificationProfileId"', response)
                except:
                    self.Error(['Invalid Message Template IDs'])
        else:
            self.Error(['Login Failed'])

    def SetBellSchedule(self, value, qualifier):

        bellID = qualifier['Bell Schedule ID']
        ringID = qualifier['Ring List ID']
        startDate = qualifier['Start Date']
        endDate = qualifier['End Date']

        if bellID and ringID and startDate and endDate:
            dataString = OrderedDict()
            dataString["ringListId"] = ringID
            dataString["startDate"] = startDate
            dataString["endDate"] = endDate
            self.__SetHelper('BellSchedule', value, qualifier, url='bell-schedules/{}'.format(bellID), data=str(dict(dataString)).encode())
        else:
            self.Discard('Invalid Command for SetBellSchedule')

    def UpdateNotifications(self, value, qualifier):
        res = self.__UpdateHelper('Notifications', value, qualifier, url='notifications?limit=10')
        if res:
            try:
                values = re.findall(self.messageTemplateRegex, res)
                for i in self.messageTemplateIds:
                    self.WriteStatus('Notifications', values.count(i), {'Message Template ID': i})
            except (ValueError, IndexError):
                self.Error(['All Notifications: Invalid/unexpected response'])

    def SetSendNotification(self, value, qualifier):

        messageID = qualifier['Message Template ID']
        subject = qualifier['Subject']

        if messageID and subject:
            dataString = json.dumps({'subject': subject, 'messageTemplateId': messageID}).encode()
            self.__SetHelper('SendNotification', value, qualifier, url='notifications', data=dataString)
        else:
            self.Discard('Invalid Command for SetSendNotification')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        if 'unauthorized' in res:
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        url = '{}api/v1/{}'.format(self.RootURL.replace('http', 'http').replace(':80', ':80'), url)
        headers = {'Authorization': 'Bearer {}'.format(self._UserToken), 'Content-Type': 'application/json'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        method = 'POST' if command != 'BellSchedule' else 'PUT'
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            res = urllib.request.urlopen(my_request)  # open() returns a http.client.HTTPResponse object if successful
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
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if command != 'Login' and command != 'MessageTemplateId':
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False
    
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
        
        url = '{}api/v1/{}'.format(self.RootURL.replace('http', 'http').replace(':80', ':80'), url)
        headers = {'Authorization': 'Bearer {}'.format(self._UserToken), 'Content-Type': 'application/json'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = urllib.request.urlopen(my_request)  # open() returns a http.client.HTTPResponse object if successful
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
        self.messageTemplateIds = []

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
