import re
import base64
import urllib.error
import urllib.request
from struct import pack


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        if deviceUsername and devicePassword:
            authentication = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            authentication.add_password(None, self.RootURL, deviceUsername, devicePassword)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler(authentication))
        else:
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler())

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Brightness': {'Status': {}},
            'ContinuousPanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'ContinuousZoom': {'Parameters': ['Speed'], 'Status': {}},
            'PanTilt': {'Status': {}},
            'PanTiltSpeed': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        self._update_brightness_regex = re.compile('brightness=(?P<brightness>[0-9]{1,4})')
        self._update_pan_tilt_speed = re.compile('speed=(1?[0-9]{1,2})')
        self._update_zoom_regex = re.compile('zoom=(?P<zoom>[0-9]{1,4})')

    def SetBrightness(self, value, qualifier):

        if 1 <= value <= 9999:
            BrightnessCmdString = '/ptz.cgi?brightness={0}'.format(value)
            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = '/ptz.cgi?query=position'
        res = self.__UpdateHelper('Brightness', value, qualifier, url=BrightnessCmdString)
        if res:
            try:
                BrightnessMatch = self._update_brightness_regex.search(res)
                if BrightnessMatch:
                    value = int(BrightnessMatch.group('brightness'))
                    if 1 <= value <= 9999:
                        self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Brightness: Invalid/unexpected response'])
            try:
                ZoomMatch = self._update_zoom_regex.search(res)
                if ZoomMatch:
                    value = int(ZoomMatch.group('zoom'))
                    if 1 <= value <= 9999:
                        self.WriteStatus('Zoom', value, qualifier)
            except (AttributeError, ValueError):
                self.Error(['Zoom: Invalid/unexpected response'])

    def SetContinuousPanTilt(self, value, qualifier):

        if 1 <= int(qualifier['Speed']) <= 100:
            ValueStateValues = {
                'Up': '/ptz.cgi?continuouspantiltmove=0,{0}'.format(qualifier['Speed']),
                'Down': '/ptz.cgi?continuouspantiltmove=0,-{0}'.format(qualifier['Speed']),
                'Left': '/ptz.cgi?continuouspantiltmove=-{0},0'.format(qualifier['Speed']),
                'Right': '/ptz.cgi?continuouspantiltmove={0},0'.format(qualifier['Speed']),
                'Up-Left': '/ptz.cgi?continuouspantiltmove=-{0},{0}'.format(qualifier['Speed']),
                'Up-Right': '/ptz.cgi?continuouspantiltmove={0},{0}'.format(qualifier['Speed']),
                'Down-Left': '/ptz.cgi?continuouspantiltmove=-{0},-{0}'.format(qualifier['Speed']),
                'Down-Right': '/ptz.cgi?continuouspantiltmove={0},-{0}'.format(qualifier['Speed']),
                'Stop': '/ptz.cgi?continuouspantiltmove=0,0'
            }

            if value in ValueStateValues:
                ContinuousPanTiltCmdString = ValueStateValues[value]
                self.__SetHelper('ContinuousPanTilt', value, qualifier, url=ContinuousPanTiltCmdString)
            else:
                self.Discard('Invalid Command for SetContinuousPanTilt')
        else:
            self.Discard('Invalid Command for SetContinuousPanTilt')

    def SetContinuousZoom(self, value, qualifier):

        if 1 <= int(qualifier['Speed']) <= 100:
            ValueStateValues = {
                'Tele': '/ptz.cgi?continuouszoommove={0}'.format(qualifier['Speed']),
                'Wide': '/ptz.cgi?continuouszoommove=-{0}'.format(qualifier['Speed']),
                'Stop': '/ptz.cgi?continuouszoommove=0'
            }

            if value in ValueStateValues:
                ContinuousZoomCmdString = ValueStateValues[value]
                self.__SetHelper('ContinuousZoom', value, qualifier, url=ContinuousZoomCmdString)
            else:
                self.Discard('Invalid Command for SetContinuousZoom')
        else:
            self.Discard('Invalid Command for SetContinuousZoom')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Up-Left': 'upleft',
            'Up-Right': 'upright',
            'Down-Left': 'downleft',
            'Down-Right': 'downright',
            'Stop': 'stop',
            'Home': 'home'
        }

        if value in ValueStateValues:
            PanTiltCmdString = '/ptz.cgi?move={0}'.format(ValueStateValues[value])
            self.__SetHelper('PanTilt', value, qualifier, url=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltSpeed(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PanTiltSpeedCmdString = '/ptz.cgi?speed={0}'.format(value)
            self.__SetHelper('PanTiltSpeed', value, qualifier, url=PanTiltSpeedCmdString)
        else:
            self.Discard('Invalid Command for SetPanTiltSpeed')

    def UpdatePanTiltSpeed(self, value, qualifier):

        PanTiltSpeedCmdString = '/ptz.cgi?query=speed'
        res = self.__UpdateHelper('PanTiltSpeed', value, qualifier, url=PanTiltSpeedCmdString)
        if res:
            try:
                valueMatch = self._update_pan_tilt_speed.search(res)
                value = valueMatch.group(1)
                if 1 <= int(value) <= 100:
                    self.WriteStatus('PanTiltSpeed', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Pan Tilt Speed: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PresetRecallCmdString = '/ptz.cgi?gotoserverpresetno={0}'.format(value)
            self.__SetHelper('PresetRecall', value, qualifier, url=PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PresetSaveCmdString = '/ptzconfig.cgi?setserverpresetno={0}'.format(value)
            self.__SetHelper('PresetSave', value, qualifier, url=PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        if 1 <= value <= 9999:
            ZoomCmdString = '/ptz.cgi?zoom={0}'.format(value)
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/axis-cgi/com{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/plain'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}/axis-cgi/com{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/plain'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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

    def AsciiHexToAscii(value):

        return int(value, 16)

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