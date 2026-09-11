import base64
import re
import urllib.error
import urllib.request
from extronlib.system import ProgramLog


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
            'AnalogInput': {'Parameters': ['Number'], 'Status': {}},
            'Counter': {'Parameters': ['Number'], 'Status': {}},
            'DigitalInput': {'Parameters': ['Number'], 'Status': {}},
            'Heartbeat': {'Status': {}},
            'Relay': {'Parameters': ['Number'], 'Status': {}},
        }

    def UpdateAnalogInput(self, value, qualifier):
        self.UpdateAllStatus(value, qualifier)

    def SetCounter(self, value, qualifier):

        counterNumber = int(qualifier['Number'])
        if 0 <= value <= 65535 and 1 <= counterNumber <= 8:
            CounterCmdString = 'protect/assignio/counter1.htm?num={0}&counter={1}'.format(counterNumber - 1, value)
            self.__SetHelper('Counter', value, qualifier, url=CounterCmdString)
        else:
            self.Discard('Invalid Command for SetCounter')

    def UpdateCounter(self, value, qualifier):
        self.UpdateAllStatus(value, qualifier)

    def UpdateDigitalInput(self, value, qualifier):
        self.UpdateAllStatus(value, qualifier)

    def UpdateAllStatus(self, value, qualifier):

        RelayStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        DigitalInputStateValues = {
            'up': 'Active',
            'dn': 'Inactive'
        }

        HeartbeatCmdString = 'globalstatus.xml'
        res = self.__UpdateHelper('Heartbeat', value, qualifier, HeartbeatCmdString)
        if res:
            try:
                relayResponse = re.findall('<led(\d+)>([01])</led(\d+)>', res)
                for i in range(0, 32):
                    qualifier = {'Number': str(int(relayResponse[i][0]) + 1)}
                    value = RelayStateValues[relayResponse[i][1]]
                    self.WriteStatus('Relay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Relay: Invalid/unexpected response'])

            try:
                digitalInputResponse = re.findall('<btn(\d+)>(up|dn)</btn(\d+)>', res)
                for i in range(0, 32):
                    qualifier = {'Number': str(int(digitalInputResponse[i][0]) + 1)}
                    value = DigitalInputStateValues[digitalInputResponse[i][1]]
                    self.WriteStatus('DigitalInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Digital Input: Invalid/unexpected response'])

            try:
                analogInputResponse = re.findall('<analog(\d)>(\d+)</analog(\d)>', res)
                for i in range(0, 4):
                    qualifier = {'Number': str(int(analogInputResponse[i][0]) + 1)}
                    value = int(analogInputResponse[i][1])
                    self.WriteStatus('AnalogInput', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Analog Input: Invalid/unexpected response'])

            try:
                counterResponse = re.findall('<count(\d)>(\d+)</count(\d)>', res)
                for i in range(0, 8):
                    qualifier = {'Number': str(int(counterResponse[i][0]) + 1)}
                    value = int(counterResponse[i][1])
                    self.WriteStatus('Counter', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Counter: Invalid/unexpected response'])

    def SetRelay(self, value, qualifier):

        relayNumber = int(qualifier['Number'])
        if 1 <= relayNumber <= 32:
            ValueStateValues = {
                'Open': '0',
                'Close': '1'
            }

            RelayCmdString = 'preset.htm?set{0}={1}'.format(relayNumber, ValueStateValues[value])
            self.__SetHelper('Relay', value, qualifier, url=RelayCmdString)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):
        self.UpdateAllStatus(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}/{}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception:
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception:
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
