import base64
from json import loads
import urllib.error
import urllib.request
from extronlib.system import ProgramLog, Timer

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
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
            'ClearRequestToSpeakListAndSpeakersList': {'Status': {}},
            'ManualLogin': {'Status': {}},
            'Microphone': {'Parameters': ['Mic'], 'Status': {}},
            'Power': {'Status': {}},
            'Recording': {'Status': {}},
            'RequestToSpeakList': {'Parameters': ['Index'], 'Status': {}},
            'SpeakersList': {'Parameters': ['Index'], 'Status': {}},
        }

        self.sid = ''

    def SetLogin(self, value, qualifier):
        Login = '{{"override": true,"username":"{}","password":"{}"}}'.format(self.deviceUsername, self.devicePassword)
        opener = self.Opener
        opener.add_handler(urllib.request.HTTPCookieProcessor())
        my_request = urllib.request.Request(''.join([self.RootURL, 'api/login']), data=Login.encode(), headers={'Content-Type': 'application/json'}, method='POST')

        try:
            res = opener.open(my_request, timeout=5)
            if res:
                res = res.getheaders()
                for i in res:
                    if i[0] == 'sid':
                        self.sid = i[1]
        except BaseException:
            self.Error(['Error obtaining sid'])

    def SetClearRequestToSpeakListAndSpeakersList(self, value, qualifier):

        self.__SetHelper('ClearRequestToSpeakListAndSpeakersList', value, qualifier, url='api/speakers', data=None, method='DELETE')

    def SetManualLogin(self, value, qualifier):

        self.SetLogin(None, None)

    def SetMicrophone(self, value, qualifier):

        Methods = {
            'Open': 'POST',
            'Close': 'DELETE',
        }

        mic = int(qualifier['Mic'])
        if 1 <= mic <= 140 and value in ('Open', 'Close'):
            if value == 'Open':
                MicrophoneCmdString = 'api/speakers'
                MicrophoneData = '[{0}]'.format(mic).encode()
            else:
                MicrophoneCmdString = 'api/speakers/{0}'.format(mic)
                MicrophoneData = None

            self.__SetHelper('Microphone', value, qualifier, url=MicrophoneCmdString, data=MicrophoneData, method=Methods[value])
        else:
            self.Discard('Invalid Command for SetMicrophone')

    def UpdateMicrophone(self, value, qualifier):


        res = self.__UpdateHelper('Microphone', value, qualifier, url='api/speakers')
        if res:
            res = res.read().decode()
            res = loads(res)

            Ids = {a['id'] for a in res}
            Difference = set(range(1, 141)) - Ids
            for a in Ids:
                self.WriteStatus('Microphone', 'Open', {'Mic': str(a)})
            for a in Difference:
                self.WriteStatus('Microphone', 'Close', {'Mic': str(a)})
        else:
            self.Error(['Microphone: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On': b'{"state":0}',
            'Standby': b'{"state":1}',
        }

        if value in States:
            self.__SetHelper('Power', value, qualifier, url='api/system/status', data=States[value], method='PUT')
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        States = {
            0: 'On',
            1: 'Standby'
        }

        res = self.__UpdateHelper('Power', value, qualifier, url='api/system/status')
        if res:
            try:
                res = loads(res.read().decode())
                value = States[res['state']]
                self.WriteStatus('Power', value, qualifier)
            except KeyError:
                self.Error(['Power: Invalid/unexpected response'])

    def SetRecording(self, value, qualifier):

        States = {
            'Start': b'{"status":1}',
            'Stop': b'{"status":0}'
        }

        if value in States:
            self.__SetHelper('Recording', value, qualifier, url='api/recorder/status', data=States[value], method='PUT')
        else:
            self.Discard('Invalid Command for SetRecording')

    def UpdateRecording(self, value, qualifier):

        States = {
            1: 'Start',
            0: 'Stop'
        }

        res = self.__UpdateHelper('Recording', value, qualifier, url='api/recorder/status')
        if res:
            try:
                res = loads(res.read().decode())
                value = States[res['status']]
                self.WriteStatus('Recording', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Recording: Invalid/unexpected response'])

    def UpdateRequestToSpeakList(self, value, qualifier):

        res = self.__UpdateHelper('RequestToSpeakList', value, qualifier, url='api/waiting-list')
        if res:

            try:
                res = res.read().decode()
                res = loads(res)

                for i in range(1, 26):
                    if i > len(res):
                        self.WriteStatus('RequestToSpeakList', '0', {'Index': str(i)})
                    else:
                        value = str(res[i - 1]['id'])
                        self.WriteStatus('RequestToSpeakList', value, {'Index': str(i)})
            except BaseException:
                self.Error(['Request To Speak List: Invalid/unexpected response'])

    def UpdateSpeakersList(self, value, qualifier):

        res = self.__UpdateHelper('SpeakersList', value, qualifier, url='api/speakers')
        if res:

            try:
                res = res.read().decode()
                res = loads(res)

                for i in range(1, 26):
                    if i > len(res):
                        self.WriteStatus('SpeakersList', '0', {'Index': str(i)})
                    else:
                        value = str(res[i - 1]['id'])
                        self.WriteStatus('SpeakersList', value, {'Index': str(i)})
            except BaseException:
                self.Error(['Speakers List: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, value, qualifier, url, data, method):

        self.Debug = True

        headers = {'Content-Type': 'application/json'}

        if command in ['Power', 'Recording']:
            if self.sid == '':
                self.Error(['Set Power missing sid value'])
            else:
                headers['sid'] = self.sid

        my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers=headers, method=method)
        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            if err.code == 401:
                self.SetLogin(None, None)
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
            elif res.status == 401:
                self.SetLogin(None, None)
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

        my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers={'Content-Type': 'application/json'})

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            if err.code == 401:
                self.SetLogin(None, None)
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
            elif res.status == 401:
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                self.SetLogin(None, None)
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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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