import urllib.error
import urllib.request
import base64
import re
from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

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
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
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
        self._update_error_regex = re.compile(r'Error:[\s\S]*$')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = '/ptz.cgi?brightness={0}'.format(value)
            self.__SetHelper('Brightness', value, qualifier, BrightnessCmdString, None)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        PositionCmdString = '/ptz.cgi?query=position'
        res = self.__UpdateHelper('Brightness', value, qualifier, PositionCmdString, None)
        if res:
            try:
                BrightnessMatch = self._update_brightness_regex.search(res)
                if BrightnessMatch:
                    self.WriteStatus('Brightness', int(BrightnessMatch.group('brightness')), qualifier)
            except (AttributeError, ValueError):
                self.Error(['Brightness: Invalid/unexpected response'])
            try:
                ZoomMatch = self._update_zoom_regex.search(res)
                if ZoomMatch:
                    self.WriteStatus('Zoom', int(ZoomMatch.group('zoom')), qualifier)
            except (AttributeError, ValueError):
                self.Error(['Zoom: Invalid/unexpected response'])

    def SetContinuousPanTilt(self, value, qualifier):

        if 1 <= int(qualifier['Speed']) <= 100:
            speed = qualifier['Speed']

            ValueStateValues = {
                'Up': '/ptz.cgi?continuouspantiltmove=0,{0}'.format(speed),
                'Down': '/ptz.cgi?continuouspantiltmove=0,-{0}'.format(speed),
                'Left': '/ptz.cgi?continuouspantiltmove=-{0},0'.format(speed),
                'Right': '/ptz.cgi?continuouspantiltmove={0},0'.format(speed),
                'Up-Left': '/ptz.cgi?continuouspantiltmove=-{0},{0}'.format(speed),
                'Up-Right': '/ptz.cgi?continuouspantiltmove={0},{0}'.format(speed),
                'Down-Left': '/ptz.cgi?continuouspantiltmove=-{0},-{0}'.format(speed),
                'Down-Right': '/ptz.cgi?continuouspantiltmove={0},-{0}'.format(speed),
                'Stop': '/ptz.cgi?continuouspantiltmove=0,0'
            }

            ContinuousPanTiltCmdString = ValueStateValues[value]
            self.__SetHelper('ContinuousPanTilt', value, qualifier, ContinuousPanTiltCmdString, None)
        else:
            self.Discard('Invalid Command for SetContinuousPanTilt')

    def SetContinuousZoom(self, value, qualifier):

        if 1 <= int(qualifier['Speed']) <= 100:
            speed = qualifier['Speed']

            ValueStateValues = {
                'Tele': '/ptz.cgi?continuouszoommove={0}'.format(speed),
                'Wide': '/ptz.cgi?continuouszoommove=-{0}'.format(speed),
                'Stop': '/ptz.cgi?continuouszoommove=0'
            }

            ContinuousZoomCmdString = ValueStateValues[value]
            self.__SetHelper('ContinuousZoom', value, qualifier, ContinuousZoomCmdString, None)
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

        PanTiltCmdString = '/ptz.cgi?move={0}'.format(ValueStateValues[value])
        self.__SetHelper('PanTilt', value, qualifier, PanTiltCmdString, None)

    def SetPanTiltSpeed(self, value, qualifier):

        PanTiltSpeedCmdString = '/ptz.cgi?speed={0}'.format(value)
        self.__SetHelper('PanTiltSpeed', value, qualifier, PanTiltSpeedCmdString, None)

    def UpdatePanTiltSpeed(self, value, qualifier):

        PanTiltSpeedCmdString = '/ptz.cgi?query=speed'
        res = self.__UpdateHelper('PanTiltSpeed', value, qualifier, PanTiltSpeedCmdString, None)
        if res:
            try:
                match = self._update_pan_tilt_speed.search(res)
                if match:
                    value = match.group(1)
                    self.WriteStatus('PanTiltSpeed', value, qualifier)
            except AttributeError:
                self.Error(['Pan Tilt Speed: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 100
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PresetRecallCmdString = '/ptz.cgi?gotoserverpresetno={0}'.format(value)
            self.__SetHelper('PresetRecall', value, qualifier, PresetRecallCmdString, None)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 100
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PresetSaveCmdString = '/ptzconfig.cgi?setserverpresetno={0}'.format(value)
            self.__SetHelper('PresetSave', value, qualifier, PresetSaveCmdString, None)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoomCmdString = '/ptz.cgi?zoom={0}'.format(value)
            self.__SetHelper('Zoom', value, qualifier, ZoomCmdString, None)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):
        self.UpdateBrightness(value, qualifier)
        
    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/axis-cgi/com{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
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
            if res.status not in (200, 202, 204):
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
        headers = {}
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
