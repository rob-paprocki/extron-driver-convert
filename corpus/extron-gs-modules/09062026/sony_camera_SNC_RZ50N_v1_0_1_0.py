import re
import base64
import urllib.error
import urllib.request


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
            'ExposureMode': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetClear': {'Status': {}},
            'PresetRecall': {'Parameters': ['Speed'], 'Status': {}},
            'PresetSave': {'Status': {}},
            'WhiteboardMode': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
        }

    def SetExposureMode(self, value, qualifier):

        if value in ['Full', 'Shutter', 'Manual']:
            ExposureModeCmdString = 'camera.cgi?ExpMode={0}'.format(value.lower())
            self.__SetHelper('ExposureMode', value, qualifier, ExposureModeCmdString)
        else:
            print('Invalid Command for SetExposureMode')

    def SetFocus(self, value, qualifier):

        focusSpd = int(qualifier['Focus Speed'])
        if value in ['Near', 'Far', 'Auto', 'Stop'] and 1 <= focusSpd <= 8:
            if value == 'Auto':
                FocusCmdString = 'ptzf.cgi?Move=onepushaf,{0}'.format(focusSpd)
            elif value == 'Stop':
                FocusCmdString = 'ptzf.cgi?Move=stop,focus'
            else:
                FocusCmdString = 'ptzf.cgi?Move={0},{1}'.format(value.lower(), focusSpd)
            self.__SetHelper('Focus', value, qualifier, FocusCmdString, None)
        else:
            print('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        if value in ['Auto', 'Manual']:
            FocusModeCmdString = 'camera.cgi?FocusMode={0}'.format(value.lower())
            self.__SetHelper('FocusMode', value, qualifier, FocusModeCmdString, None)
        else:
            print('Invalid Command for SetFocusMode')

    def SetPanTilt(self, value, qualifier):

        pantilt = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Up Left': 'up-left',
            'Up Right': 'up-right',
            'Down Left': 'down-left',
            'Down Right': 'down-right',
            'Stop': 'stop'
        }[value]

        pantiltSpd = int(qualifier['Pan Tilt Speed'])
        if 1 <= pantiltSpd <= 24:
            if pantilt == 'stop':
                PanTiltCmdString = 'ptzf.cgi?Move=stop,motor'
            else:
                PanTiltCmdString = 'ptzf.cgi?Move={0},{1}'.format(pantilt, pantiltSpd)
            self.__SetHelper('PanTilt', value, qualifier, PanTiltCmdString, None)
        else:
            print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        if value in ['On', 'Off']:
            PowerCmdString = 'system.cgi?PowerLed={0}'.format(value.lower())
            self.__SetHelper('Power', value, qualifier, PowerCmdString, None)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'inq=system&inq=camera'
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString)
        if res:
            try:
                power = re.search('PowerLed=(on|off)', res)
                self.WriteStatus('Power', power.group(1).title(), qualifier)
            except IndexError:
                print('Power: Invalid/unexpected response')
            try:
                expMode = re.search('ExpMode=(full|shutter|manual)', res)
                self.WriteStatus('ExposureMode', expMode.group(1).title(), qualifier)
            except IndexError:
                print('ExposureMode: Invalid/unexpected response')
            try:
                focusMode = re.search('FocusMode=(auto|manual)', res)
                self.WriteStatus('FocusMode', focusMode.group(1).title(), qualifier)
            except IndexError:
                print('FocusMode: Invalid/unexpected response')
            try:
                wbMode = re.search('WBMode=(auto|indoor|outdoor|onepushwb|manual)', res)
                if wbMode.group(1) == 'onepushwb':
                    self.WriteStatus('WhiteboardMode', 'One Push', qualifier)
                else:
                    self.WriteStatus('WhiteboardMode', wbMode.group(1).title(), qualifier)
            except IndexError:
                print('WhiteboardMode: Invalid/unexpected response')

    def SetPresetClear(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetClearCmdString = 'presetposition.cgi?PresetClear={0}'.format(value)
            self.__SetHelper('PresetClear', value, qualifier, PresetClearCmdString, None)
        else:
            print('Invalid Command for SetPresetClear')

    def SetPresetRecall(self, value, qualifier):

        speed = int(qualifier['Speed'])
        if 1 <= int(value) <= 16 and 1 <= speed <= 24:
            PresetRecallCmdString = 'presetposition.cgi?PresetCall={0},{1}'.format(value, speed)
            self.__SetHelper('PresetRecall', value, qualifier, PresetRecallCmdString, None)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = 'presetposition.cgi?PresetSet={0}'.format(value)
            self.__SetHelper('PresetSave', value, qualifier, PresetSaveCmdString, None)
        else:
            print('Invalid Command for SetPresetSave')

    def SetWhiteboardMode(self, value, qualifier):

        wbMode = {
            'Auto': 'auto',
            'Indoor': 'indoor',
            'Outdoor': 'outdoor',
            'One Push': 'onepushwb',
            'Manual': 'manual'
        }[value]

        WhiteboardModeCmdString = 'camera.cgi?WBMode={0}'.format(wbMode)
        self.__SetHelper('WhiteboardMode', value, qualifier, WhiteboardModeCmdString)

    def SetZoom(self, value, qualifier):

        zoomSpd = int(qualifier['Zoom Speed'])
        if value in ['Tele', 'Wide', 'Stop'] and 1 <= zoomSpd <= 8:
            if value == 'Stop':
                ZoomCmdString = 'ptzf.cgi?Move=stop,zoom'
            else:
                ZoomCmdString = 'ptzf.cgi?Move={0},{1}'.format(value.lower(), zoomSpd)
            self.__SetHelper('Zoom', value, qualifier, ZoomCmdString, None)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/command/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}

        my_request = urllib.request.Request(url, data=None, headers=headers)

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        url = '{0}/command/inquiry.cgi?{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
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
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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
