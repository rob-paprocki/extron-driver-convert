import base64
import urllib.error
import urllib.request
import json

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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'Output': {'Parameters': ['Number'], 'Status': {}},
        }


    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def UpdateFirmwareVersion(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        FirmwareVersionCmdString = 'statusjsn.js?components=17'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=FirmwareVersionCmdString)
        if res:

            try:
                value = res['misc']['firm_v']
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

            try:
                for counter, output in enumerate(res['outputs']):
                    qualifier = dict()
                    qualifier['Number'] = '{}{}'.format('A' if counter < 6 else 'B',
                                                        counter + 1 if counter < 6 else counter - 5)
                    value = ValueStateValues[output['state']]
                    self.WriteStatus('Output', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetOutput(self, value, qualifier):

        NumberStates = {
            'Min': 1,
            'Max': 12,
        }

        try:
            if qualifier['Number'][0] in ('A', 'B') and 1 <= int(qualifier['Number'][1]) <= 6:
                NumberStates['Value'] = int(qualifier['Number'][1]) + (0 if qualifier['Number'][0] == 'A' else 6)
            else:
                NumberStates['Value'] = -1
        except (IndexError, ValueError):
            NumberStates['Value'] = -1

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        if self.__constraint_checker(NumberStates) and value in ValueStateValues:
            OutputCmdString = 'ov.html?cmd=1$p={}&s={}'.format(NumberStates['Value'], ValueStateValues[value])
            self.__SetHelper('Output', value, qualifier, OutputCmdString)
        else:
            self.Discard('Invalid Command for SetOutput')

    def UpdateOutput(self, value, qualifier):
        self.UpdateFirmwareVersion(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        if res:
            json_output = json.loads(res)
            try:
                res = json_output if json_output['eof'] == 1 else dict()
            except (KeyError, IndexError):
                res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}

        my_request = urllib.request.Request(url, data=None, headers=headers)

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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

            url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
            headers = {}

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])
