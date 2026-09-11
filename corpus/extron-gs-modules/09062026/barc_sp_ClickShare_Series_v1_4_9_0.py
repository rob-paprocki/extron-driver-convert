from extronlib.system import GetUnverifiedContext
from extronlib.system import ProgramLog, Wait
from json import loads, dumps
import urllib.error
import urllib.request
import base64

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername='integrator', devicePassword='integrator', SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.port = port

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        if self.port == 4001:  # HTTPS
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else:  # HTTP Digest
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
            
        urllib.request.install_opener(self.Opener)

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'CSM-1 ClickShare': self.barc_18_1668_CSM,
            'CSC-1 ClickShare': self.barc_18_1668_CSC,
            'CSE-200 ClickShare': self.barc_18_1668_CSE,
            'CSE-200+ ClickShare': self.barc_18_1668_CSE_plus,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioOutput': {'Status': {}},
            'ButtonConnectionStatus': {'Parameters': ['Button'], 'Status': {}},
            'ButtonCountStatus': {'Status': {}},
            'Configuration': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'DisplayResolution': {'Parameters': ['Output'], 'Status': {}},
            'DisplayStandby': {'Status': {}},
            'EnableOutput': {'Parameters': ['Output'], 'Status': {}},
            'OnScreenText': {'Parameters': ['Display Item'], 'Status': {}},
            'Source': {'Status': {}},
            'SourceSharing': {'Status': {}},
            'StandbyMode': {'Status': {}},
            'WLANSSID': {'Status': {}},
            'WLANWebEnabled': {'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        AudioMuteCmdString = 'v1.0/Audio/Enabled'
        jsonData = dumps(
            {'value': ValueStateValues[value]}
        )
        self.__SetHelper('AudioMute', value, qualifier, AudioMuteCmdString, jsonData.encode())

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            True: 'On',
            False: 'Off'
        }

        resource = '/v1.0/Audio/Enabled'
        res = self.__UpdateHelper('AudioMute', value, qualifier, resource)
        if res:
            try:
                value = ValueStateValues[res['data']['value']]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAudioOutput(self, value, qualifier):

        ValueStateValues = {
            'Analog': 'Analog',
            'Digital': 'Digital'
        }

        AudioOutputCmdString = self.AudioOutput
        jsonData = dumps(
            {"value": ValueStateValues[value]}
        )
        self.__SetHelper('AudioOutput', value, qualifier, AudioOutputCmdString, jsonData.encode())

    def UpdateAudioOutput(self, value, qualifier):

        ValueStateValues = {
            'Analog': 'Analog',
            'Digital': 'Digital'
        }

        AudioOutputCmdString = '/{}'.format(self.AudioOutput)
        res = self.__UpdateHelper('AudioOutput', value, qualifier, AudioOutputCmdString)
        if res:
            try:
                value = self.AudioOutputStates[res['data']['value']]
                self.WriteStatus('AudioOutput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Output: Invalid/unexpected response'])

    def UpdateButtonConnectionStatus(self, value, qualifier):

        ValueStateValues = {
            True: 'Connected',
            False: 'Disconnected'
        }
        if 1 <= int(qualifier['Button']) <= self.MaxNumberofButtons:
            ButtonConnectionStatusCmdString = '/v1.0/Buttons/ButtonTable/{}/Connected'.format(qualifier['Button'])
            res = self.__UpdateHelper('ButtonConnectionStatus', value, qualifier, ButtonConnectionStatusCmdString)
            if res:
                try:
                    value = ValueStateValues[res['data']['value']]
                    self.WriteStatus('ButtonConnectionStatus', value, qualifier)
                except (KeyError, ValueError, IndexError):
                    self.Error(['Button Connection Status: Invalid/unexpected response'])
            else:
                self.WriteStatus('ButtonConnectionStatus', 'Not Configured', qualifier)
        else:
            self.Discard('Inappropriate Command for UpdateButtonConnectionStatus')

    def UpdateButtonCountStatus(self, value, qualifier):

        ButtonCountStatusCmdString = '/v1.0/Buttons/ButtonCount'
        res = self.__UpdateHelper('ButtonCountStatus', value, qualifier, ButtonCountStatusCmdString)
        if res:
            try:
                value = res['data']['value']
                if 0 <= int(value) <= self.MaxNumberofButtons:
                    self.WriteStatus('ButtonCountStatus', str(value), qualifier)
                else:
                    self.Error(['Button Count Status: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Button Count Status: Invalid/unexpected response'])

    def SetConfiguration(self, value, qualifier):

        ValueStateValues = {
            'Restart': 'RestartSystem',
            'Shutdown': 'ShutdownSystem'
        }

        ConfigurationCmdString = 'v1.0/Configuration/{0}'.format(ValueStateValues[value])
        jsonData = dumps(
            {"value": "true"}
        )
        self.__SetHelper('Configuration', value, qualifier, ConfigurationCmdString, jsonData.encode())

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Extended': 'Extended',
            'Clone': 'Clone'
        }

        DisplayModeCmdString = 'v1.0/Display/Mode'
        jsonData = dumps(
            {"value": ValueStateValues[value]}
        )
        self.__SetHelper('DisplayMode', value, qualifier, DisplayModeCmdString, jsonData.encode())

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Extended': 'Extended',
            'Clone': 'Clone'
        }

        DisplayModeCmdString = '/v1.0/Display/Mode'
        res = self.__UpdateHelper('DisplayMode', value, qualifier, DisplayModeCmdString)
        if res:
            try:
                value = ValueStateValues[res['data']['value']]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Mode: Invalid/unexpected response'])

    def SetDisplayResolution(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            '1280x720': '1280x720',
            '1920x1080': '1920x1080',
            '800x600': '800x600',
            '1024x768': '1024x768',
            '1280x768': '1280x768',
            '1280x800': '1280x800',
            '1360x768': '1360x768',
            '1440x900': '1440x900',
            'Auto'    : 'Auto'
        }

        if self.model in ['CSM', 'CSE']:
            DisplayResolutionCmdString = 'v1.0/Display/OutputTable/1/Resolution'
            jsonData = dumps(
                {"value": ValueStateValues[value]}
            )
            self.__SetHelper('DisplayResolution', value, qualifier, DisplayResolutionCmdString, jsonData.encode())
        else:
            Output = OutputStates[qualifier['Output']]

            DisplayResolutionCmdString = 'v1.0/Display/OutputTable/{0}/Resolution'.format(Output)
            jsonData = dumps(
                {"value": ValueStateValues[value]}
            )
            self.__SetHelper('DisplayResolution', value, qualifier, DisplayResolutionCmdString, jsonData.encode())

    def UpdateDisplayResolution(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            '1280x720': '1280x720',
            '1920x1080': '1920x1080',
            '800x600': '800x600',
            '1024x768': '1024x768',
            '1280x768': '1280x768',
            '1280x800': '1280x800',
            '1360x768': '1360x768',
            '1440x900': '1440x900'
        }

        if self.model in ['CSM', 'CSE']:
            DisplayResolutionCmdString = '/v1.0/Display/OutputTable/1/Resolution'
            res = self.__UpdateHelper('DisplayResolution', value, qualifier, DisplayResolutionCmdString)
            if res:
                try:
                    value = ValueStateValues[res['data']['value']]
                    self.WriteStatus('DisplayResolution', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Display Resolution: Invalid/unexpected response'])
        else:
            Output = OutputStates[qualifier['Output']]

            DisplayResolutionCmdString = '/v1.0/Display/OutputTable/{0}/Resolution'.format(Output)
            res = self.__UpdateHelper('DisplayResolution', value, qualifier, DisplayResolutionCmdString)
            if res:
                try:
                    value = ValueStateValues[res['data']['value']]
                    self.WriteStatus('DisplayResolution', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Display Resolution: Invalid/unexpected response'])

    def SetDisplayStandby(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        DisplayStandbyCmdString = 'v1.0/Display/StandbyState'
        jsonData = dumps(
            {"value": ValueStateValues[value]}
        )
        self.__SetHelper('DisplayStandby', value, qualifier, DisplayStandbyCmdString, jsonData.encode())

    def UpdateDisplayStandby(self, value, qualifier):

        ValueStateValues = {
            True: 'On',
            False: 'Off'
        }

        DisplayStandbyCmdString = '/v1.0/Display/StandbyState'
        res = self.__UpdateHelper('DisplayStandby', value, qualifier, DisplayStandbyCmdString)
        if res:
            try:
                value = ValueStateValues[res['data']['value']]
                self.WriteStatus('DisplayStandby', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Standby: Invalid/unexpected response'])

    def SetEnableOutput(self, value, qualifier):

        States = {
            'On': 'true',
            'Off': 'false'
        }
        if self.model == 'CSC':
            OutputStates = {
                '1': '1',
                '2': '2'
            }

            Output = OutputStates[qualifier['Output']]

            CmdString = 'v1.0/Display/OutputTable/{}/Enabled'.format(Output)
            jsonData = dumps(
                {"value": States[value]}
            )

            self.__SetHelper('EnableOutput', value, qualifier, CmdString, jsonData.encode())

        elif self.model == 'CSE':

            CmdString = 'v1.0/Display/OutputTable/1/Enabled'
            jsonData = dumps(
                {"value": States[value]}
            )

            self.__SetHelper('EnableOutput', value, qualifier, CmdString, jsonData.encode())

    def UpdateEnableOutput(self, value, qualifier):

        States = {
            True: 'On',
            False: 'Off'
        }

        if self.model == 'CSC':
            OutputStates = {
                '1': '1',
                '2': '2'
            }

            Output = OutputStates[qualifier['Output']]

            CmdString = '/v1.0/Display/OutputTable/{}/Enabled'.format(Output)
            res = self.__UpdateHelper('EnableOutput', value, qualifier, CmdString)
            if res:
                try:
                    value = States[res['data']['value']]
                    self.WriteStatus('EnableOutput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Enable Output: Invalid/unexpected response'])

        elif self.model == 'CSE':
            CmdString = '/v1.0/Display/OutputTable/1/Enabled'
            res = self.__UpdateHelper('EnableOutput', value, qualifier, CmdString)
            if res:
                try:
                    value = States[res['data']['value']]
                    self.WriteStatus('EnableOutput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Enable Output: Invalid/unexpected response'])

    def SetInputCard(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'true', 
            'Disable' : 'false'
        }

        InputCardCmdString = 'v1.10/InputCard/InputTable/1/Enabled'
        jsonData = dumps(
                        {"value":ValueStateValues[value]}
                        )
        self.__SetHelper('InputCard', value, qualifier, InputCardCmdString, jsonData.encode())

    def UpdateInputCard(self, value, qualifier):

        ValueStateValues = {
            True  : 'Enable', 
            False : 'Disable'
        }

        InputCardCmdString = '/v1.10/InputCard/InputTable/1/Enabled'
        res = self.__UpdateHelper('InputCard', value, qualifier, InputCardCmdString)
        if res:
            try:
                value = ValueStateValues[res['data']['value']]
                self.WriteStatus('InputCard', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input Card: Invalid/unexpected response'])

    def UpdateOnScreenText(self, value, qualifier):

        DisplayItemStates = {
            'Language': 'Language',
            'Location': 'Location',
            'Meeting Room Name': 'MeetingRoomName',
            'Welcome Message': 'WelcomeMessage'
        }

        display_item = DisplayItemStates[qualifier['Display Item']]
        OnScreenTextCmdString = '/v1.0/OnScreenText'
        res = self.__UpdateHelper('OnScreenText', value, qualifier, OnScreenTextCmdString)
        if res:
            try:
                value = res['data']['value'][display_item]
                self.WriteStatus('OnScreenText', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Text: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'v1.0/Configuration/RestartSystem'
        jsonData = dumps(
                        {"value":"true"}
                        )
        self.__SetHelper('Reboot', value, qualifier, RebootCmdString, jsonData.encode())

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            True: 'Connected',
            False: 'Disconnected'
        }

        SourceCmdString = '/v1.0/DeviceInfo/InUse'
        res = self.__UpdateHelper('Source', value, qualifier, SourceCmdString)
        if res:
            try:
                value = ValueStateValues[res['data']['value']]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source: Invalid/unexpected response'])

    def UpdateSourceSharing(self, value, qualifier):

        ValueStateValues = {
            True: 'Sharing Content',
            False: 'No Content'
        }

        SourceSharingCmdString = '/v1.0/DeviceInfo/Sharing'
        res = self.__UpdateHelper('SourceSharing', value, qualifier, SourceSharingCmdString)
        if res:
            try:
                value = ValueStateValues[res['data']['value']]
                self.WriteStatus('SourceSharing', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source Sharing: Invalid/unexpected response'])

    def SetStandbyMode(self, value, qualifier):

        StandbyModeCmdString = 'v1.5/Standby/EnergyMode'
        jsonData = dumps(
                        {"value":self.StandbyModeStates[value]}
                        )
        self.__SetHelper('StandbyMode', value, qualifier, StandbyModeCmdString, jsonData.encode())

    def _cmd_UpdateStandbyMode(self, value, qualifier):
        """Update Standby Mode
        value: Enum
        qualifier: None
        """
        StandbyModeCmdString = '/v1.5/Standby/EnergyMode'
        res = self.__UpdateHelper('StandbyMode', value, qualifier, StandbyModeCmdString)
        if res:
            try:
                value = self.StandbyModeValues[res['data']['value']]
                self.WriteStatus('StandbyMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Standby Mode: Invalid/unexpected response'])

    def UpdateWLANSSID(self, value, qualifier):

        WLANSSIDCmdString = '/v1.0/Network/Wlan/Ssid'
        res = self.__UpdateHelper('WLANSSID', value, qualifier, WLANSSIDCmdString)
        if res:
            try:
                value = res['data']['value']
                self.WriteStatus('WLANSSID', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['WLAN SSID: Invalid/unexpected response'])

    def SetWLANWebEnabled(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        WLANWebEnabledCmdString = 'v1.0/RemoteManagement/WlanWebEnabled'
        jsonData = dumps(
            {"value": ValueStateValues[value]}
        )
        self.__SetHelper('WLANWebEnabled', value, qualifier, WLANWebEnabledCmdString, jsonData.encode())

    def UpdateWLANWebEnabled(self, value, qualifier):

        ValueStateValues = {
            True: 'On',
            False: 'Off'
        }

        WLANWebEnabledCmdString = '/v1.0/RemoteManagement/WlanWebEnabled'
        res = self.__UpdateHelper('WLANWebEnabled', value, qualifier, WLANWebEnabledCmdString)
        if res:
            try:
                value = ValueStateValues[res['data']['value']]
                self.WriteStatus('WLANWebEnabled', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['WLAN Web Enabled: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response:
            res = loads(response.read().decode())
            return res

    def digestOpenerBuilder(self, url):
        passmgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, url, self.deviceUsername, self.devicePassword)
        return urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler(passmgr))

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}

        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            if self.port == 4001:
                res = self.Opener.open(my_request, timeout=1)
            else:
                res = self.digestOpenerBuilder(url).open(my_request, timeout=1)
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

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {}

        authHandler = '{0}:{1}'.format(self.deviceUsername, self.devicePassword).encode()
        authHeader = base64.b64encode(authHandler).decode("ascii")
        headers['Authorization'] = 'Basic {}'.format(authHeader)
        headers['Content-Type'] = 'application/json'

        my_request = urllib.request.Request(url, data=data, headers=headers)  # method defaults to GET when data is None

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        try:
            if self.port == 4001:
                res = self.Opener.open(my_request, timeout=1)
            else:
                res = self.digestOpenerBuilder(url).open(my_request, timeout=1)
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

    def barc_18_1668_CSC(self):
        self.AudioOutput = 'v1.0/Audio/Output'
        self.AudioOutputStates = {
            'Analog' : 'Analog',
            'Digital': 'Digital'
        }
        self.MaxNumberofButtons = 64
        self.model = 'CSC'

    def barc_18_1668_CSE(self):
        self.AudioOutput = 'v1.5/Audio/Output'
        self.AudioOutputStates = {
            'Jack' : 'Jack',
            'HDMI' : 'HDMI',
            'SPDIF': 'SPDIF'
        }

        self.MaxNumberofButtons = 16

        self.StandbyModeStates = {
            'Eco' : 'eco_standby',
            'Deep' : 'deep_standby'
        }

        self.StandbyModeValues = {
            'eco_standby' : 'Eco',
            'deep_standby' : 'Deep'
        }
        self.model = 'CSE'

    def barc_18_1668_CSE_plus(self):
        self.AudioOutput = 'v1.5/Audio/Output'
        self.AudioOutputStates = {
            'Jack': 'Jack',
            'HDMI': 'HDMI',
            'SPDIF': 'SPDIF'
        }

        self.MaxNumberofButtons = 16

        self.StandbyModeStates = {
            'Eco': 'eco_standby',
            'Network': 'networked_standby',
            'Deep': 'deep_standby'
        }

        self.StandbyModeValues = {
            'eco_standby': 'Eco',
            'networked_standby': 'Network',
            'deep_standby': 'Deep'
        }
        self.model = 'CSE'

    def barc_18_1668_CSM(self):
        self.MaxNumberofButtons = 8
        self.model = 'CSM'

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
                    except BaseException:
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
        except BaseException:
            return None


class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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