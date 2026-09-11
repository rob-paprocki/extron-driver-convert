import urllib.error
import urllib.request
import base64
import json

class DeviceClass:

    def __init__(self,ipAddress, port, deviceUsername=None, devicePassword=None):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self._NetworkName = 'unsecured'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'GroupIntensity': {'Parameters': ['Group ID', 'Fade Time'], 'Status': {}},
            'GroupSceneRecall': {'Parameters': ['Group ID', 'Fade Time'], 'Status': {}},
            'Intensity': {'Parameters': ['Device ID'], 'Status': {}},
            'IntensitywithFading': {'Parameters': ['Device ID', 'Fade Time'], 'Status': {}},
            'SceneRecall': {'Parameters': ['Device ID'], 'Status': {}},
            'SceneRecallwithFading': {'Parameters': ['Device ID', 'Fade Time'], 'Status': {}},
            'Temperature': {'Status': {}},
        }

        self.queryDelay = 0

    @property
    def NetworkName(self):
        return self._NetworkName

    @NetworkName.setter
    def NetworkName(self, value):
        self._NetworkName = value

    def SetGroupIntensity(self, value, qualifier):

        if 0 <= value <= 100 and 0 <= qualifier['Fade Time'] <= 14400000 and 0 <= qualifier['Group ID'] <= 16382:
            GroupIntensityCmdString = 'device/setintensity/{0}/{1}/{2}/{3}'.format(self._NetworkName, int(qualifier['Group ID'] + 0xC000), value, qualifier['Fade Time'])
            self.__SetHelper('GroupIntensity', value, qualifier, GroupIntensityCmdString)
        else:
            self.Discard('Invalid Command for SetGroupIntensity')

    def SetGroupSceneRecall(self, value, qualifier):

        if 0 <= value <= 65535 and 0 <= qualifier['Fade Time'] <= 14400000 and 0 <= qualifier['Group ID'] <= 16382:
            GroupSceneRecallCmdString = 'device/recallscene/{0}/{1}/{2}/{3}'.format(self._NetworkName, int(qualifier['Group ID'] + 0xC000), value, qualifier['Fade Time'])
            self.__SetHelper('GroupSceneRecall', value, qualifier, GroupSceneRecallCmdString)
        else:
            self.Discard('Invalid Command for SetGroupSceneRecall')

    def SetIntensity(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Device ID']:
            IntensityCmdString = 'device/setintensity/{0}/{1}/{2}'.format(self._NetworkName, qualifier['Device ID'], value)
            self.__SetHelper('Intensity', value, qualifier, IntensityCmdString, queryDelay=10)
        else:
            self.Discard('Invalid Command for SetIntensity')

    def UpdateIntensity(self, value, qualifier):

        if qualifier['Device ID']:
            IntensityCmdString = 'device/details/{0}/{1}'.format(self._NetworkName, qualifier['Device ID'])
            res = self.__UpdateHelper('Intensity', value, qualifier, IntensityCmdString)
            if res:
                try:
                    value = round(float(json.loads(res)['04. Intensity']), 1)
                    self.WriteStatus('Intensity', value, qualifier)
                except (ValueError, KeyError):
                    self.Error(['Intensity: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateIntensity')

    def SetIntensitywithFading(self, value, qualifier):

        if 0 <= value <= 100 and 0 <= qualifier['Fade Time'] <= 14400000 and qualifier['Device ID']:
            IntensitywithFadingCmdString = 'device/setintensity/{0}/{1}/{2}/{3}'.format(self._NetworkName, qualifier['Device ID'], value, qualifier['Fade Time'])
            self.__SetHelper('IntensitywithFading', value, qualifier, IntensitywithFadingCmdString)
        else:
            self.Discard('Invalid Command for SetIntensitywithFading')

    def SetSceneRecall(self, value, qualifier):

        if 0 <= value <= 65535 and qualifier['Device ID']:
            SceneRecallCmdString = 'device/recallscene/{0}/{1}/{2}'.format(self._NetworkName, qualifier['Device ID'], value)
            self.__SetHelper('SceneRecall', value, qualifier, SceneRecallCmdString)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

    def SetSceneRecallwithFading(self, value, qualifier):

        if 0 <= value <= 65535 and 0 <= qualifier['Fade Time'] <= 14400000 and qualifier['Device ID']:
            SceneRecallCmdString = 'device/recallscene/{0}/{1}/{2}/{3}'.format(self._NetworkName, qualifier['Device ID'], value, qualifier['Fade Time'])
            self.__SetHelper('SceneRecallwithFading', value, qualifier, SceneRecallCmdString)
        else:
            self.Discard('Invalid Command for SetSceneRecallwithFading')

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'gateway_info'
        res = self.__UpdateHelper('Temperature', value, qualifier, TemperatureCmdString)
        if res:
            try:
                value = float('{0:1f}'.format(float(json.loads(res)['temperature'])))
                self.WriteStatus('Temperature', value, qualifier)
            except (ValueError, KeyError):
                self.Error(['Temperature: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url, queryDelay=0):
        self.Debug = True

        if queryDelay > 0:
            self.queryDelay = queryDelay
        url = '{0}{1}'.format(self.RootURL, url)
        headers = {}
        myRequest = urllib.request.Request(url, data=None, headers=headers)

        try:
            res = self.Opener.open(myRequest)  # open() returns a http.client.HTTPResponse object if successful
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

        if self.queryDelay > 0:
            self.queryDelay = self.queryDelay - 1
        elif self.queryDelay == 0:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            url = '{0}{1}'.format(self.RootURL, url)
            headers = {}
            myRequest = urllib.request.Request(url, data=data, headers=headers)

            try:
                res = self.Opener.open(myRequest)  # open() returns a http.client.HTTPResponse object if successful
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
                    res = self.__CheckResponseForErrors(command, res)  # __CheckResponseForErrors returns res.read().decode()
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