from json import loads, dumps
import urllib.error
import urllib.request
import base64


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.RootURL, deviceUsername, devicePassword)
        self.auth_handler = urllib.request.HTTPDigestAuthHandler(passman)
        self.Opener = urllib.request.build_opener(self.auth_handler)
        urllib.request.install_opener(self.Opener)

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Channel': {'Status': {}},
            'SplitMode': {'Status': {}},
        }

    def SetChannel(self, value, qualifier):

        if 1 <= int(value) <= 64:
            Channel = int(value) - 1
            CmdString = 'splitMode=1X1&channel={}'.format(Channel)
            self.__SetHelper('Channel', value, qualifier, CmdString)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetSplitMode(self, value, qualifier):

        States = {
            '1X1': '1X1',
            '2X1': '2X1',
            '2X2': '2X2',
            '3X1': '3X3',
            '3X3': '4X4',
            '4X4': '4X4',
            '5X5': '5X5',
            '6X6': '6X6',
            '1+5': '1+5',
            '1+7': '1+7',
            '1+12': '1+12'
        }

        CmdString = 'splitMode={}'.format(States[value])
        self.__SetHelper('SplitMode', value, qualifier, CmdString)

    def UpdateSplitMode(self, value, qualifier):

        States = {
            'SplitMode=1X1': '1X1',
            'SplitMode=2X1': '2X1',
            'SplitMode=2X2': '2X2',
            'SplitMode=3X1': '3X3',
            'SplitMode=3X3': '4X4',
            'SplitMode=4X4': '4X4',
            'SplitMode=5X5': '5X5',
            'SplitMode=6X6': '6X6',
            'SplitMode=1+5': '1+5',
            'SplitMode=1+7': '1+7',
            'SplitMode=1+12': '1+12'
        }

        res = self.__UpdateHelper('SplitMode', value, qualifier, None)
        if res:
            self.WriteStatus('SplitMode', States[res], qualifier)
            try:
                self.WriteStatus('SplitMode', States[res], qualifier)
            except (TypeError, IndexError):
                self.Error(['Split Mode: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True

        url = '{}/stw-cgi/display.cgi?msubmenu=layout&action=update&{}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'text/html'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request)
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

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        url = '{}/stw-cgi/display.cgi?msubmenu=layout&action=view'.format(self.RootURL)
        headers = {'Content-Type': 'text/html'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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
