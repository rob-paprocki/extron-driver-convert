import base64
import urllib.error
import urllib.request
from re import compile, search

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        if deviceUsername is not None and devicePassword is not None:
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
            'AutoFocus': {'Status': {}},
            'AutoIris': {'Status': {}},
            'Backlight': {'Status': {}},
            'Brightness': {'Status': {}},
            'ContinuousFocus': {'Parameters': ['Speed'], 'Status': {}},
            'ContinuousPanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'ContinuousZoom': {'Parameters': ['Speed'], 'Status': {}},
            'Focus': {'Status': {}},
            'IRCutFilter': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Status': {}},
            'PanTiltSpeed': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        self.MatchAutoFocus = compile('autofocus=(?P<autofocus>on|off)')
        self.MatchAutoIris = compile('autoiris=(?P<autoiris>on|off)')
        self.MatchBrightness = compile('brightness=(?P<brightness>[0-9]{1,4})')
        self.MatchIris = compile('iris=(?P<iris>[0-9]{1,4})')
        self.MatchFocus = compile('focus=(?P<focus>[0-9]{3,4})')
        self.MatchPanTiltSpeed = compile('speed=(1?[0-9]{1,2})')
        self.MatchZoom = compile('zoom=(?P<zoom>1?[0-9]{1,4})')
        self.MatchError = compile(r'Error:[\s\S]*$')

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
        }

        if value in ValueStateValues:
            AutoFocusCmdString = 'autofocus={}'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', value, qualifier, url=AutoFocusCmdString)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = 'query=position'
        res = self.__UpdateHelper('AutoFocus', value, qualifier, url=AutoFocusCmdString)
        if res:
            try:
                AutoFocusMatch = self.MatchAutoFocus.search(res)
                if AutoFocusMatch:
                    self.WriteStatus('AutoFocus', AutoFocusMatch.group('autofocus').capitalize(), qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

            try:
                AutoIrisMatch = self.MatchAutoIris.search(res)
                if AutoIrisMatch:
                    self.WriteStatus('AutoIris', AutoIrisMatch.group('autoiris').capitalize(), qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Iris: Invalid/unexpected response'])

            try:
                BrightnessMatch = self.MatchBrightness.search(res)
                if BrightnessMatch:
                    self.WriteStatus('Brightness', int(BrightnessMatch.group('brightness')), qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Brightness: Invalid/unexpected response'])

            try:
                FocusMatch = self.MatchFocus.search(res)
                if FocusMatch:
                    self.WriteStatus('Focus', int(FocusMatch.group('focus')), qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Focus: Invalid/unexpected response'])

            try:
                IrisMatch = self.MatchIris.search(res)
                if IrisMatch:
                    self.WriteStatus('Iris', int(IrisMatch.group('iris')), qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Iris: Invalid/unexpected response'])

            try:
                ZoomMatch = self.MatchZoom.search(res)
                if ZoomMatch:
                    self.WriteStatus('Zoom', int(ZoomMatch.group('zoom')), qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Zoom: Invalid/unexpected response'])

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
        }

        if value in ValueStateValues:
            AutoIrisCmdString = 'autoiris={}'.format(ValueStateValues[value])
            self.__SetHelper('AutoIris', value, qualifier, url=AutoIrisCmdString)
        else:
            self.Discard('Invalid Command for SetAutoIris')

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
        }

        if value in ValueStateValues:
            BacklightCmdString = 'backlight={}'.format(ValueStateValues[value])
            self.__SetHelper('Backlight', value, qualifier, url=BacklightCmdString)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            BrightnessCmdString = 'brightness={}'.format(value)
            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetContinuousFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 100,
            'Value': int(qualifier['Speed']) if qualifier['Speed'].isdigit() else -1,
        }

        ValueStateValues = {
            'Far': 'continuousfocusmove={}',
            'Near': 'continuousfocusmove=-{}',
            'Stop': 'continuousfocusmove=0',
        }

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Stop':
                ContinuousFocusCmdString = ValueStateValues[value]
            else:
                ContinuousFocusCmdString = ValueStateValues[value].format(SpeedConstraints['Value'])
            self.__SetHelper('ContinuousFocus', value, qualifier, url=ContinuousFocusCmdString)
        else:
            self.Discard('Invalid Command for SetContinuousFocus')

    def SetContinuousPanTilt(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 100,
            'Value': int(qualifier['Speed']) if qualifier['Speed'].isdigit() else -1,
        }

        ValueStateValues = {
            'Up': 'continuouspantiltmove=0,{}',
            'Down': 'continuouspantiltmove=0,-{}',
            'Left': 'continuouspantiltmove=-{},0',
            'Right': 'continuouspantiltmove={},0',
            'Up-Left': 'continuouspantiltmove=-{},{}',
            'Up-Right': 'continuouspantiltmove={},{}',
            'Down-Left': 'continuouspantiltmove=-{},-{}',
            'Down-Right': 'continuouspantiltmove={},-{}',
            'Stop': 'continuouspantiltmove=0,0',
        }

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Stop':
                ContinuousPanTiltCmdString = ValueStateValues[value]
            elif value in ('Up', 'Down', 'Left', 'Right'):
                ContinuousPanTiltCmdString = ValueStateValues[value].format(SpeedConstraints['Value'])
            else:
                ContinuousPanTiltCmdString = ValueStateValues[value].format(SpeedConstraints['Value'], SpeedConstraints['Value'])
            self.__SetHelper('ContinuousPanTilt', value, qualifier, url=ContinuousPanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetContinuousPanTilt')

    def SetContinuousZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 100,
            'Value': int(qualifier['Speed']) if qualifier['Speed'].isdigit() else -1,
        }

        ValueStateValues = {
            'Tele': 'continuouszoommove={0}',
            'Wide': 'continuouszoommove=-{0}',
            'Stop': 'continuouszoommove=0'
        }

        if value in ValueStateValues:
            if value == 'Stop':
                ContinuousZoomCmdString = ValueStateValues[value]
            else:
                ContinuousZoomCmdString = ValueStateValues[value].format(SpeedConstraints['Value'])
            self.__SetHelper('ContinuousZoom', value, qualifier, url=ContinuousZoomCmdString)
        else:
            self.Discard('Invalid Command for SetContinuousZoom')

    def SetFocus(self, value, qualifier):

        ValueConstraints = {
            'Min': 770,
            'Max': 9999,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            FocusCmdString = 'focus={}'.format(ValueConstraints['Value'])
            self.__SetHelper('Focus', value, qualifier, url=FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIRCutFilter(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
            'Auto': 'auto',
        }

        if value in ValueStateValues:
            IRCutFilterCmdString = 'ircutfilter={}'.format(ValueStateValues[value])
            self.__SetHelper('IRCutFilter', value, qualifier, url=IRCutFilterCmdString)
        else:
            self.Discard('Invalid Command for SetIRCutFilter')

    def SetIris(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            IrisCmdString = 'iris={}'.format(ValueConstraints['Value'])
            self.__SetHelper('Iris', value, qualifier, url=IrisCmdString)
        else:
            self.Discard('Invalid Command for SetIris')

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
            'Home': 'home',
        }

        if value in ValueStateValues:
            PanTiltCmdString = 'move={}'.format(ValueStateValues[value])
            self.__SetHelper('PanTilt', value, qualifier, url=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltSpeed(self, value, qualifier):

        ValueStateConstraints = {
            'Min': 1,
            'Max': 100,
            'Value': int(value) if value.isdigit() else -1
        }

        if self.__constraint_checker(ValueStateConstraints):
            PanTiltSpeedCmdString = 'speed={}'.format(ValueStateConstraints['Value'])
            self.__SetHelper('PanTiltSpeed', value, qualifier, url=PanTiltSpeedCmdString)
        else:
            self.Discard('Invalid Command for SetPanTiltSpeed')

    def UpdatePanTiltSpeed(self, value, qualifier):

        PanTiltSpeedCmdString = 'query=speed'
        res = self.__UpdateHelper('PanTiltSpeed', value, qualifier, url=PanTiltSpeedCmdString)
        if res:
            try:
                match = self.MatchPanTiltSpeed.search(res)
                if match:
                    value = match.group(1)
                    if value == '0':
                        value = '1'
                    self.WriteStatus('PanTiltSpeed', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Pan Tilt Speed: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 256,
            'Value': int(value) if value.isdigit() else -1,
        }

        if self.__constraint_checker(ValueConstraints):
            PresetRecallCmdString = 'gotoserverpresetno={}'.format(ValueConstraints['Value'])
            self.__SetHelper('PresetRecall', value, qualifier, url=PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 256,
            'Value': int(value) if value.isdigit() else -1,
        }

        if self.__constraint_checker(ValueConstraints):
            PresetSaveCmdString = 'setserverpresetno={}'.format(ValueConstraints['Value'])
            self.__SetHelper('PresetSave', value, qualifier, url=PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            ZoomCmdString = 'zoom={}'.format(ValueConstraints['Value'])
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}/axis-cgi/com/ptz.cgi?{}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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

        url = '{}/axis-cgi/com/ptz.cgi?{}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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
