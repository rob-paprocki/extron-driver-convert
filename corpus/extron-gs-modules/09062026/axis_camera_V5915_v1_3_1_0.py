import re
import base64
import urllib.error
import urllib.request


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, Model):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        if Model == 'V5915 Basic Authentication':
            if deviceUsername and devicePassword:
                self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
            else:
                self.authentication = None
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
        else:
            if deviceUsername and devicePassword:
                authentication = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                authentication.add_password(None, self.RootURL, deviceUsername, devicePassword)
                self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler(authentication))
            else:
                self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False

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
            'Position': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        self.MatchAutoFocus = re.compile('autofocus=(?P<autofocus>on|off)')
        self.MatchAutoIris = re.compile('autoiris=(?P<autoiris>on|off)')
        self.MatchBrightness = re.compile('brightness=(?P<brightness>[0-9]{1,4})')
        self.MatchIris = re.compile('iris=(?P<iris>[0-9]{1,4})')
        self.MatchFocus = re.compile('focus=(?P<focus>[0-9]{3,4})')
        self.MatchPanTiltSpeed = re.compile('speed=(1?[0-9]{1,2})')
        self.MatchZoom = re.compile('zoom=(?P<zoom>1?[0-9]{1,4})')
        self.MatchError = re.compile('Error:[\s\S]*$')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        AutoFocusCmdString = 'autofocus=' + ValueStateValues[value]
        self.__SetHelper('AutoFocus', value, qualifier, AutoFocusCmdString, None)

    def UpdateAutoFocus(self, value, qualifier):

        self.UpdatePosition(value, qualifier)

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        AutoIrisCmdString = 'autoiris=' + ValueStateValues[value]
        self.__SetHelper('AutoIris', value, qualifier, AutoIrisCmdString, None)

    def UpdateAutoIris(self, value, qualifier):

        self.UpdatePosition(value, qualifier)

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        BacklightCmdString = 'backlight=' + ValueStateValues[value]
        self.__SetHelper('Backlight', value, qualifier, BacklightCmdString, None)

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = 'brightness=' + str(value)
            self.__SetHelper('Brightness', value, qualifier, BrightnessCmdString, None)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        self.UpdatePosition(value, qualifier)

    def SetContinuousFocus(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStatesValue = {
            'Far': 'continuousfocusmove={0}'.format(speed),
            'Near': 'continuousfocusmove=-{0}'.format(speed),
            'Stop': 'continuousfocusmove=0'
        }

        if 1 <= speed <= 100:
            ContinuousFocusCmdString = ValueStatesValue[value]
            self.__SetHelper('ContinuousFocus', value, qualifier, ContinuousFocusCmdString, None)
        else:
            self.Discard('Invalid Command for SetContinuousFocus')

    def SetContinuousPanTilt(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStatesValue = {
            'Up': 'continuouspantiltmove=0,{0}'.format(speed),
            'Down': 'continuouspantiltmove=0,-{0}'.format(speed),
            'Left': 'continuouspantiltmove=-{0},0'.format(speed),
            'Right': 'continuouspantiltmove={0},0'.format(speed),
            'Up-Left': 'continuouspantiltmove=-{0},{1}'.format(speed, speed),
            'Up-Right': 'continuouspantiltmove={0},{1}'.format(speed, speed),
            'Down-Left': 'continuouspantiltmove=-{0},-{1}'.format(speed, speed),
            'Down-Right': 'continuouspantiltmove={0},-{1}'.format(speed, speed),
            'Stop': 'continuouspantiltmove=0,0'
        }

        if 1 <= speed <= 100:
            ContinuousPanTiltCmdString = ValueStatesValue[value]
            self.__SetHelper('ContinuousPanTilt', value, qualifier, ContinuousPanTiltCmdString, None)
        else:
            self.Discard('Invalid Command for SetContinuousPanTilt')

    def SetContinuousZoom(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStatesValue = {
            'Tele': 'continuouszoommove={0}'.format(speed),
            'Wide': 'continuouszoommove=-{0}'.format(speed),
            'Stop': 'continuouszoommove=0'
        }

        if 1 <= speed <= 100:
            ContinuousZoomCmdString = ValueStatesValue[value]
            self.__SetHelper('ContinuousZoom', value, qualifier, ContinuousZoomCmdString, None)
        else:
            self.Discard('Invalid Command for SetContinuousZoom')

    def SetFocus(self, value, qualifier):

        ValueConstraints = {
            'Min': 770,
            'Max': 9999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FocusCmdString = 'focus=' + str(value)
            self.__SetHelper('Focus', value, qualifier, FocusCmdString, None)
        else:
            self.Discard('Invalid Command for SetFocus')

    def UpdateFocus(self, value, qualifier):

        self.UpdatePosition(value, qualifier)

    def SetIRCutFilter(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
            'Auto': 'auto'
        }

        IRCutFilterCmdString = 'ircutfilter=' + ValueStateValues[value]
        self.__SetHelper('IRCutFilter', value, qualifier, IRCutFilterCmdString, None)

    def SetIris(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            IrisCmdString = 'iris=' + str(value)
            self.__SetHelper('Iris', value, qualifier, IrisCmdString, None)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        self.UpdatePosition(value, qualifier)

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

        PanTiltCmdString = 'move=' + ValueStateValues[value]
        self.__SetHelper('PanTilt', value, qualifier, PanTiltCmdString, None)

    def SetPanTiltSpeed(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 100
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PanTiltSpeedCmdString = 'speed=' + value
            self.__SetHelper('PanTiltSpeed', value, qualifier, PanTiltSpeedCmdString, None)
        else:
            self.Discard('Invalid Command for SetPanTiltSpeed')

    def UpdatePanTiltSpeed(self, value, qualifier):

        PanTiltSpeedCmdString = 'query=speed'
        res = self.__UpdateHelper('PanTiltSpeed', value, qualifier, PanTiltSpeedCmdString, None)
        if res:
            try:
                match = self.MatchPanTiltSpeed.search(res)
                if match:
                    value = match.group(1)

                    if value == '0':
                        value = '1'

                    self.WriteStatus('PanTiltSpeed', value, qualifier)
            except (KeyError, IndexError):
                pass

    def UpdatePosition(self, value, qualifier):

        PositionCmdString = 'query=position'
        res = self.__UpdateHelper('Position', value, qualifier, PositionCmdString, None)
        if res:
            try:
                AutoFocusMatch = self.MatchAutoFocus.search(res)
                if AutoFocusMatch:
                    self.WriteStatus('AutoFocus', AutoFocusMatch.group('autofocus').capitalize(), qualifier)
            except (KeyError, IndexError, AttributeError):
                pass

            try:
                AutoIrisMatch = self.MatchAutoIris.search(res)
                if AutoIrisMatch:
                    self.WriteStatus('AutoIris', AutoIrisMatch.group('autoiris').capitalize(), qualifier)
            except (KeyError, IndexError, AttributeError):
                pass

            try:
                BrightnessMatch = self.MatchBrightness.search(res)
                if BrightnessMatch:
                    self.WriteStatus('Brightness', int(BrightnessMatch.group('brightness')), qualifier)
            except (KeyError, IndexError, AttributeError):
                pass

            try:
                IrisMatch = self.MatchIris.search(res)
                if IrisMatch:
                    self.WriteStatus('Iris', int(IrisMatch.group('iris')), qualifier)
            except (KeyError, IndexError, AttributeError):
                pass

            try:
                FocusMatch = self.MatchFocus.search(res)
                if FocusMatch:
                    self.WriteStatus('Focus', int(FocusMatch.group('focus')), qualifier)
            except (KeyError, IndexError, AttributeError):
                pass

            try:
                ZoomMatch = self.MatchZoom.search(res)
                if ZoomMatch:
                    self.WriteStatus('Zoom', int(ZoomMatch.group('zoom')), qualifier)
            except (KeyError, IndexError, AttributeError):
                pass

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 256
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PresetRecallCmdString = 'gotoserverpresetno=' + value
            self.__SetHelper('PresetRecall', value, qualifier, PresetRecallCmdString, None)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 256
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PresetSaveCmdString = 'setserverpresetno=' + value
            self.__SetHelper('PresetSave', value, qualifier, PresetSaveCmdString, None)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoomCmdString = 'zoom=' + str(value)
            self.__SetHelper('Zoom', value, qualifier, ZoomCmdString, None)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        self.UpdatePosition(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None,):
        self.Debug = True

        url = '{0}/axis-cgi/com/ptz.cgi?{1}'.format(self.RootURL.rstrip('/'), url)
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        url = '{0}/axis-cgi/com/ptz.cgi?{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')
        res = ''
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
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, Model)
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
