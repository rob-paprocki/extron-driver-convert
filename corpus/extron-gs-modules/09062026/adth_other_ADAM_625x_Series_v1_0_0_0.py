import base64
import urllib.error
import urllib.request
import extronlib.standard.exml.etree.ElementTree as ET


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername='root', devicePassword='00000000'):

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
        self.Models = {
            'ADAM-6250': self.adth_31_5724_6250,
            'ADAM-6251': self.adth_31_5724_6251,
            'ADAM-6256': self.adth_31_5724_6256,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DigitalInputStatus': {'Parameters': ['Channel'], 'Status': {}},
            'DigitalOutputStatus': {'Parameters': ['Channel'], 'Status': {}},
        }

    def UpdateDigitalInputStatus(self, value, qualifier):

        if 0 <= int(qualifier['Channel']) <= self.InputMax:
            cmdString = 'digitalinput/all/value'
            res = self.__UpdateHelper('DigitalInputStatus', value, qualifier, url=cmdString)
            if res:
                try:
                    ValueStateValues = {
                        '1': 'On',
                        '0': 'Off'
                    }

                    for chnl in res.findall('DI'):
                        qualifier = {'Channel': chnl.find('ID').text}
                        value = ValueStateValues[chnl.find('VALUE').text]
                        self.WriteStatus('DigitalInputStatus', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['Digital Input Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDigitalInputStatus')

    def UpdateDigitalOutputStatus(self, value, qualifier):

        if 0 <= int(qualifier['Channel']) <= self.OutputMax:
            cmdString = 'digitaloutput/all/value'
            res = self.__UpdateHelper('DigitalOutputStatus', value, qualifier, url=cmdString)
            if res:
                try:
                    ValueStateValues = {
                        '1': 'On',
                        '0': 'Off'
                    }

                    for chnl in res.findall('DO'):
                        qualifier = {'Channel': chnl.find('ID').text}
                        value = ValueStateValues[chnl.find('VALUE').text]
                        self.WriteStatus('DigitalOutputStatus', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['Digital Output Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDigitalOutputStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        root = ET.fromstring(response.read())
        try:
            status = root.attrib['status']
            if status == 'OK':
                return root
            else:
                self.Error(['Error occurred: {}'.format(status)])
        except (KeyError, AttributeError):
            self.Error(['Invalid/unexpected response'])

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        pass

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url)  # self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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

    def adth_31_5724_6250(self):
        self.InputMax = 7
        self.OutputMax = 6

    def adth_31_5724_6251(self):
        self.InputMax = 15

    def adth_31_5724_6256(self):
        self.OutputMax = 15

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
