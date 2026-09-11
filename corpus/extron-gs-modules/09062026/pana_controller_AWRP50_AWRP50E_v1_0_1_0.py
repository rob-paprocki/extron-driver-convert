from re import compile
import urllib.error
import urllib.request
import base64


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.IPAddress = ipAddress
        self.port = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        self.auth_handler = urllib.request.HTTPBasicAuthHandler()
        self.Opener = urllib.request.build_opener(self.auth_handler)
        urllib.request.install_opener(self.Opener)

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CameraSwitching': {'Status': {}},
            'CameraSwitchingwithGroupPort': {'Parameters': ['Port'], 'Status': {}},
        }

        self.Cam = compile('XQC:01:([0-9]{1,3})')
        self.Port = compile('XQC:02:([0-9]{1,2}):([1-5])')

    def SetCameraSwitching(self, value, qualifier):

        if 1 <= int(value) <= 100:
            data = 'cmd=XCN:01:{0}&res=1'.format(value)
            self.__SetHelper('CameraSwitching', value, qualifier, url='', data=data)
        else:
            print('Invalid Command for SetCameraSwitching')

    def UpdateCameraSwitching(self, value, qualifier):

        data = 'cmd=XQC:01&res=1'
        res = self.__UpdateHelper('CameraSwitching', value, qualifier, url='', data=data)
        if res:
            try:
                cam = self.Cam.search(res)
                if cam is not None:
                    value = cam.group(1)
                else:
                    value = ''
                self.WriteStatus('CameraSwitching', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdateCameraSwitching')

    def SetCameraSwitchingwithGroupPort(self, value, qualifier):

        port = int(qualifier['Port'])
        if (1 <= port <= 5) and (1 <= int(value) <= 20):
            data = 'cmd=XCN:02:{0}:{1}&res=1'.format(value, port)
            self.__SetHelper('CameraSwitchingwithGroupPort', value, qualifier, url='', data=data)
        else:
            print('Invalid Command for SetCameraSwitchingwithGroupPort')

    def UpdateCameraSwitchingwithGroupPort(self, value, qualifier):

        data = 'cmd=XQC:02&res=1'
        res = self.__UpdateHelper('CameraSwitchingwithGroupPort', value, qualifier, url='', data=data)
        if res:
            try:
                temp = self.Port.search(res)
                if temp is not None:
                    value = temp.group(1)
                    qualifier['Port'] = temp.group(2)
                else:
                    value = ''
                    qualifier['Port'] = ''
                self.WriteStatus('CameraSwitchingwithGroupPort', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdateCameraSwitchingwithGroupPort')

    def __CheckResponseForErrors(self, sourceCmdName, res):
        return res.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        my_request = urllib.request.Request(url)

        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        try:
            res = self.Opener.open(my_request, headers=headers)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter += 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        my_request = urllib.request.Request(url, headers=headers)
        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
