from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import base64
import json
import urllib.error
import urllib.request
from urllib.parse import quote

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoConnectOnClientLaunch': {'Status': {}},
            'Boot': {'Status': {}},
            'BrowserConfigEnabled': {'Status': {}},
            'ClearAll': {'Status': {}},
            'CurrentLiveSourceNumber': {'Status': {}},
            'CurrentUserNumber': {'Status': {}},
            'DisplayID': {'Status': {}},
            'DisplayName': {'Status': {}},
            'EmergencyBroadcast': {'Status': {}},
            'EmergencyBroadcastTextStatus': {'Status': {}},
            'HDMIDisplayMode': { 'Status': {}},
            'HDMIInput': {'Status': {}},
            'IPAddress': {'Status': {}},
            'Language': {'Status': {}},
            'LocalConfigEnabled': {'Status': {}},
            'Reboot': {'Status': {}},
            'ResetScreenKey': {'Status': {}},
            'Restart': {'Status': {}},
            'ScreenKey': {'Status': {}},
            'SerialPassthroughCommand': { 'Status': {}},
            'ShowSplashScreen': {'Status': {}},
            'Suspend': {'Status': {}},
            'Wake': {'Status': {}},
        }

    def SetBoot(self, value, qualifier):

        if self.devicePassword:
            BootCmdString = '/api/control/boot?password={}'.format(self.devicePassword)
        else:
            BootCmdString = '/api/control/boot'

        self.__SetHelper('Boot', value, qualifier, BootCmdString)

    def SetClearAll(self, value, qualifier):

        if self.devicePassword:
            ClearAllCmdString = '/api/control/clear?password={}'.format(self.devicePassword)
        else:
            ClearAllCmdString = '/api/control/clear'

        self.__SetHelper('ClearAll', value, qualifier, ClearAllCmdString)

    def UpdateCurrentLiveSourceNumber(self, value, qualifier):

        self.UpdateCurrentUserNumber(value, qualifier)

    def UpdateCurrentUserNumber(self, value, qualifier):

        if self.devicePassword:
            CurrentUserNumberCmdString = '/api/stats?password={}'.format(self.devicePassword)
        else:
            CurrentUserNumberCmdString = '/api/stats'
        res = self.__UpdateHelper('CurrentUserNumber', value, qualifier, CurrentUserNumberCmdString)
        if res:
            try:
                value = str(res['m_statistics']['m_connectedUsers'])
                self.WriteStatus('CurrentUserNumber', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Current User Number: Invalid/unexpected response'])

            try:
                value = str(res['m_statistics']['m_currentLiveSourceCount'])
                self.WriteStatus('CurrentLiveSourceNumber', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Current Live Source Number: Invalid/unexpected response'])

    def UpdateDisplayID(self, value, qualifier):

        if self.devicePassword:
            DisplayIDCmdString = '/api/config?password={}'.format(self.devicePassword)
        else:
            DisplayIDCmdString = '/api/config'
        res = self.__UpdateHelper('DisplayID', value, qualifier, DisplayIDCmdString)
        if res:
            try:
                value = res['m_displayId']
                self.WriteStatus('DisplayID', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display ID: Invalid/unexpected response'])

            try:
                value = res['m_displayInformation']['m_displayName']
                self.WriteStatus('DisplayName', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Name: Invalid/unexpected response'])

            try:
                value = res['m_displayInformation']['m_ipv4']
                self.WriteStatus('IPAddress', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IP Address: Invalid/unexpected response'])

            try:
                value = res['m_generalCuration']['autoConnectOnClientLaunch']
                self.WriteStatus('AutoConnectOnClientLaunch', str(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Connect On Client Launch: Invalid/unexpected response'])

            try:
                value = res['m_generalCuration']['browserConfigEnabled']
                self.WriteStatus('BrowserConfigEnabled', str(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Browser Config Enabled: Invalid/unexpected response'])

            try:
                value = res['m_generalCuration']['localConfigEnabled']
                self.WriteStatus('LocalConfigEnabled', str(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Local Config Enabled: Invalid/unexpected response'])

            try:
                value = res['m_generalCuration']['language']
                self.WriteStatus('Language', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Language: Invalid/unexpected response'])

            try:
                value = res['m_authenticationCuration']['sessionKey']
                self.WriteStatus('ScreenKey', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Screen Key: Invalid/unexpected response'])

            try:
                value = res['m_generalCuration']['showSplashScreen']
                self.WriteStatus('ShowSplashScreen', str(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Show Splash Screen: Invalid/unexpected response'])

            try:
                value = res['m_networkCuration']['emergencyEnabled']
                self.WriteStatus('EmergencyBroadcast', str(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Emergency Broadcast: Invalid/unexpected response'])

            try:
                value = res['m_networkCuration']['emergencyText']
                self.WriteStatus('EmergencyBroadcastTextStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Emergency Broadcast Text Status: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    1: 'Mirror',
                    2: 'Seamless Extend',
                    3: 'Extend'
                }

                value = ValueStateValues[res['m_generalCuration']['hdmiOutDisplayMode']]
                self.WriteStatus('HDMIDisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['HDMI Display Mode: Invalid/unexpected response'])

    def SetEmergencyBroadcast(self, value, qualifier):

        EmergencyBroadcastCmdString = '/api/config'

        if self.devicePassword:
            if value == 'True':
                Text = qualifier['Text']

                if Text is not None:
                    jsonData = json.dumps({'password': str(self.devicePassword), 'm_networkCuration': {'emergencyEnabled': True, 'emergencyText': Text}})
                else:
                    self.Discard('Invalid Command for SetEmergencyBroadcast')
                    return
            elif value == 'False':
                jsonData = json.dumps({'password': str(self.devicePassword), 'm_networkCuration': {'emergencyEnabled': False}})
            else:
                self.Discard('Invalid Command for SetEmergencyBroadcast')
                return
        else:
            if value == 'True':
                Text = qualifier['Text']

                if Text is not None:
                    jsonData = json.dumps({'m_networkCuration': {'emergencyEnabled': True, 'emergencyText': Text}})
                else:
                    self.Discard('Invalid Command for SetEmergencyBroadcast')
                    return
            elif value == 'False':
                jsonData = json.dumps({'m_networkCuration': {'emergencyEnabled': False}})
            else:
                self.Discard('Invalid Command for SetEmergencyBroadcast')
                return

        self.__SetHelper('EmergencyBroadcast', value, qualifier, EmergencyBroadcastCmdString, jsonData.encode())

    def SetHDMIDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Mirror':           1,
            'Seamless Extend':  2,
            'Extend':           3
        }

        if value in ValueStateValues:
            HDMIDisplayModeCmdString = '/api/config'
            data = {
                'm_generalCuration': {
                    'hdmiOutDisplayMode': ValueStateValues[value]
                }
            }

            if self.devicePassword:
                data['password'] = self.devicePassword
            
            self.__SetHelper('HDMIDisplayMode', value, qualifier, url=HDMIDisplayModeCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetHDMIDisplayMode')

    def SetHDMIInput(self, value, qualifier):

        ValueStateValues = {
            'On': 'false',
            'Off': 'true'
        }

        if value in ValueStateValues:
            HDMIInputCmdString = '/api/config/hdmi_input'
            data = 'force_off={}'.format(ValueStateValues[value]).encode()
            self.__SetHelper('HDMIInput', value, qualifier, HDMIInputCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetHDMIInput')

    def SetReboot(self, value, qualifier):

        if self.devicePassword:
            RebootCmdString = '/api/control/reboot?password={}'.format(self.devicePassword)
        else:
            RebootCmdString = '/api/control/reboot'

        self.__SetHelper('Reboot', value, qualifier, RebootCmdString)

    def SetResetScreenKey(self, value, qualifier):

        if self.devicePassword:
            ResetScreenKeyCmdString = '/api/control/resetkey?password={}'.format(self.devicePassword)
        else:
            ResetScreenKeyCmdString = '/api/control/resetkey'

        self.__SetHelper('ResetScreenKey', value, qualifier, ResetScreenKeyCmdString)

    def SetRestart(self, value, qualifier):

        if self.devicePassword:
            RestartCmdString = '/api/control/restart?password={}'.format(self.devicePassword)
        else:
            RestartCmdString = '/api/control/restart'

        self.__SetHelper('Restart', value, qualifier, RestartCmdString)

    def SetSerialPassthroughCommand(self, value, qualifier):

        data = value

        if data:
            SerialPassthroughCommandCmdString = '/api/serial-passthru/send?data={}'.format(quote(data, encoding='iso-8859-1', safe=''))
            self.__SetHelper('SerialPassthroughCommand', value, qualifier, url=SerialPassthroughCommandCmdString)
        else:
            self.Discard('Invalid Command for SetSerialPassthroughCommand')

    def SetSuspend(self, value, qualifier):

        if self.devicePassword:
            SuspendCmdString = '/api/control/suspend?password={}'.format(self.devicePassword)
        else:
            SuspendCmdString = '/api/control/suspend'

        self.__SetHelper('Suspend', value, qualifier, SuspendCmdString)

    def SetWake(self, value, qualifier):

        if self.devicePassword:
            WakeCmdString = '/api/control/wake?password={}'.format(self.devicePassword)
        else:
            WakeCmdString = '/api/control/wake'

        self.__SetHelper('Wake', value, qualifier, WakeCmdString)

    def __CheckResponseForErrors(self, sourceCmdName, res):

        try:
            return json.loads(res.read().decode())
        except json.decoder.JSONDecodeError:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)

        if command not in ['HDMIInput', 'SerialPassthroughCommand']:
            headers = {'Content-Type': 'application/json'}
        else:
            headers = {}

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST' if command in ['EmergencyBroadcast', 'HDMIDisplayMode', 'HDMIInput'] else 'GET')

        try:
            res = self.Opener.open(my_request, timeout=10)
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
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'application/json'}
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