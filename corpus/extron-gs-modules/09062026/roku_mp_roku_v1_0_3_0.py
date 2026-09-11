import urllib.error
import urllib.request
import base64


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

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
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Keyboard': {'Status': {}},
            'LaunchCommand': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Transport': {'Status': {}},
        }

    def SetKeyboard(self, value, qualifier):

        ValueStateValues = {
            '1': 'Lit_1',
            '2': 'Lit_2',
            '3': 'Lit_3',
            '4': 'Lit_4',
            '5': 'Lit_5',
            '6': 'Lit_6',
            '7': 'Lit_7',
            '8': 'Lit_8',
            '9': 'Lit_9',
            '0': 'Lit_0',
            'a': 'Lit_a',
            'b': 'Lit_b',
            'c': 'Lit_c',
            'd': 'Lit_d',
            'e': 'Lit_e',
            'f': 'Lit_f',
            'g': 'Lit_g',
            'h': 'Lit_h',
            'i': 'Lit_i',
            'j': 'Lit_j',
            'k': 'Lit_k',
            'l': 'Lit_l',
            'm': 'Lit_m',
            'n': 'Lit_n',
            'o': 'Lit_o',
            'p': 'Lit_p',
            'q': 'Lit_q',
            'r': 'Lit_r',
            's': 'Lit_s',
            't': 'Lit_t',
            'u': 'Lit_u',
            'v': 'Lit_v',
            'w': 'Lit_w',
            'x': 'Lit_x',
            'y': 'Lit_y',
            'z': 'Lit_z',
            'Space': 'Lit_%20',
            'Backspace': 'Backspace'
        }

        KeyboardCmdString = 'keypress/{0}'.format(ValueStateValues[value])
        self.__SetHelper('Keyboard', value, qualifier, url=KeyboardCmdString)

    def SetLaunchCommand(self, value, qualifier):
        num = qualifier['Number']
        if num:
            LaunchCommandCmdString = 'launch/{0}'.format(num)
            self.__SetHelper('LaunchCommand', value, qualifier, url=LaunchCommandCmdString)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': 'left',
            'Right': 'right',
            'Up': 'up',
            'Down': 'down',
            'Select': 'select',
            'Back': 'back',
            'Enter': 'enter',
            'Home': 'home',
            'Info': 'info',
            'Search': 'search',
            'Backspace': 'backspace'
        }

        MenuNavigationCmdString = 'keypress/{0}'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', value, qualifier, url=MenuNavigationCmdString)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play/Pause': 'play',
            'Rev': 'rev',
            'Fwd': 'fwd',
            'Instant Replay': 'instantreplay'
        }

        TransportCmdString = 'keypress/{0}'.format(ValueStateValues[value])
        self.__SetHelper('Transport', value, qualifier, url=TransportCmdString)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request)  # open() returns a http.client.HTTPResponse object if successful
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

        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request)  # open() returns a http.client.HTTPResponse object if successful
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
