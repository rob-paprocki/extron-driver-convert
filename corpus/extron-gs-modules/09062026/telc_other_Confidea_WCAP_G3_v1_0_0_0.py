import base64
import urllib.error
import urllib.request
import uuid


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'MaximumActiveMicrophones': {'Status': {}},
            'MicrophoneControl': {'Status': {}},
            'MicrophoneMode': {'Status': {}},
        }

        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword

        self.SetLogin()

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetLogin(self):

        params = {
            'login': '{}'.format(self.deviceUsername),
            'password': '{}'.format(self.devicePassword),
        }
        opener = self.Opener
        opener.add_handler(urllib.request.HTTPCookieProcessor())
        headers, data = self.multipart_encoder(params)
        url = '{0}/_script/php/login.php'.format(self.RootURL.rstrip('/'))
        request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = opener.open(request)
        response.getheaders()
        response.read()

    @staticmethod
    def multipart_encoder(params):
        boundary = uuid.uuid4().hex
        lines = list()
        for key, val in params.items():
            if val:
                lines.append('--' + boundary)
                lines.append('Content-Disposition: form-data; name="{}"'.format(key))
                lines.extend(['', val])

        lines.append('--{}--'.format(boundary))

        body = bytes()
        for l in lines:
            if isinstance(l, bytes):
                body += l + b'\r\n'
            else:
                body += bytes(l, encoding='utf8') + b'\r\n'

        headers = {
            'Content-Type': 'multipart/form-data; boundary=' + boundary,
        }

        return headers, body

    def SetMaximumActiveMicrophones(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 6,
            'Value': int(value) if value.isdigit() else -1,
        }

        if self.__constraint_checker(ValueConstraints):
            MaximumActiveMicrophonesCmdString = 'set.php?mam={}'.format(ValueConstraints['Value'])
            self.__SetHelper('MaximumActiveMicrophones', value, qualifier, MaximumActiveMicrophonesCmdString)
        else:
            self.Discard('Invalid Command for SetMaximumActiveMicrophones')

    def SetMicrophoneControl(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 2048,
            'Value': qualifier['Number'],
        }

        ValueStateValues = {
            'Off': 0,
            'Active': 1,
            'Request': 2,
        }

        if value in ValueStateValues and self.__constraint_checker(NumberConstraints):
            MicrophoneControlCmdString = 'func.php?function=SetMicState&channel={}&state={}'.format(
                NumberConstraints['Value'],
                ValueStateValues[value])
            self.__SetHelper('MicrophoneControl', value, qualifier, MicrophoneControlCmdString)
        else:
            self.Discard('Invalid Command for SetMicrophoneControl')

    def SetMicrophoneMode(self, value, qualifier):

        OptionsStates = {
            'None': 0,
            'Request Allowed': 1,
            'Cancel Request Allowed': 2,
            'Use Override': 4,
        }

        ActivationTypeStates = {
            'None': 0,
            'Toggle': 1,
            'Push': 2,
            'Vox': 4,
        }

        ValueStateValues = {
            'Operator': 0,
            'Direct Speak': 1,
            'Group Request': 2,
        }

        mic_option = qualifier['Option']
        mic_act_type = qualifier['Activation Type']
        if value in ValueStateValues and mic_option in OptionsStates and mic_act_type in ActivationTypeStates:
            MicrophoneModeCmdString = 'set.php?mmo={{"mmo":{}, "mio":{}, "mat":{}}}'.format(ValueStateValues[value],
                                                                                            OptionsStates[mic_option],
                                                                                            ActivationTypeStates[mic_act_type])
            self.__SetHelper('MicrophoneMode', value, qualifier, MicrophoneModeCmdString)
        else:
            self.Discard('Invalid Command for SetMicrophoneMode')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, resource='', data=None):
        self.Debug = True

        base_url = '/_script/php/'
        url = '{0}{1}{2}'.format(self.RootURL.rstrip('/'), base_url, resource)
        headers = {'Content-Type': 'text/html'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])

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
    def __init__(self, ipAddress, port, deviceUsername='admin', devicePassword=None, Model=None):
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
