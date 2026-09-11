from extronlib.system import Wait, ProgramLog
import re
import urllib.error
import urllib.request
import json

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
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Brightness': { 'Status': {}},
            'ContinuousPanTilt': {'Parameters':['Speed'], 'Status': {}},
            'ContinuousZoom': {'Parameters':['Speed'], 'Status': {}},
            'Heater': { 'Status': {}},
            'HeaterDuration': { 'Status': {}},
            'PanTilt': { 'Status': {}},
            'PanTiltSpeed': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Wiper': {'Parameters':['Duration'], 'Status': {}},
            'Zoom': { 'Status': {}},
        }

        self._update_brightness_regex = re.compile('brightness=(?P<brightness>[0-9]{1,4})')
        self._update_pan_tilt_speed = re.compile('speed=(1?[0-9]{1,2})')
        self._update_zoom_regex = re.compile('zoom=(?P<zoom>[0-9]{1,4})')

    def SetBrightness(self, value, qualifier):

        if 1 <= value <= 9999:
            BrightnessCmdString = 'axis-cgi/com/ptz.cgi?brightness={0}'.format(value)
            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'axis-cgi/com/ptz.cgi?query=position'
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
                'Up'        : 'axis-cgi/com/ptz.cgi?continuouspantiltmove=0,{0}'.format(qualifier['Speed']),
                'Down'      : 'axis-cgi/com/ptz.cgi?continuouspantiltmove=0,-{0}'.format(qualifier['Speed']),
                'Left'      : 'axis-cgi/com/ptz.cgi?continuouspantiltmove=-{0},0'.format(qualifier['Speed']),
                'Right'     : 'axis-cgi/com/ptz.cgi?continuouspantiltmove={0},0'.format(qualifier['Speed']),
                'Up-Left'   : 'axis-cgi/com/ptz.cgi?continuouspantiltmove=-{0},{0}'.format(qualifier['Speed']),
                'Up-Right'  : 'axis-cgi/com/ptz.cgi?continuouspantiltmove={0},{0}'.format(qualifier['Speed']),
                'Down-Left' : 'axis-cgi/com/ptz.cgi?continuouspantiltmove=-{0},-{0}'.format(qualifier['Speed']),
                'Down-Right': 'axis-cgi/com/ptz.cgi?continuouspantiltmove={0},-{0}'.format(qualifier['Speed']),
                'Stop'      : 'axis-cgi/com/ptz.cgi?continuouspantiltmove=0,0'
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
                'Tele': 'axis-cgi/com/ptz.cgi?continuouszoommove={0}'.format(qualifier['Speed']),
                'Wide': 'axis-cgi/com/ptz.cgi?continuouszoommove=-{0}'.format(qualifier['Speed']),
                'Stop': 'axis-cgi/com/ptz.cgi?continuouszoommove=0'
            }

            if value in ValueStateValues:
                ContinuousZoomCmdString = ValueStateValues[value]
                self.__SetHelper('ContinuousZoom', value, qualifier, url=ContinuousZoomCmdString)
            else:
                self.Discard('Invalid Command for SetContinuousZoom')
        else:
            self.Discard('Invalid Command for SetContinuousZoom')

    def SetHeater(self, value, qualifier):

        ValueStateValues = {
            'Start' : 'axis-cgi/temperaturecontrol.cgi?device=heater&id=7&action=start',
            'Stop'  : 'axis-cgi/temperaturecontrol.cgi?device=heater&id=7&action=stop'
        }

        if value in ValueStateValues:
            HeaterCmdString = ValueStateValues[value]
            self.__SetHelper('Heater', value, qualifier, url=HeaterCmdString)
        else:
            self.Discard('Invalid Command for SetHeater')

    def SetHeaterDuration(self, value, qualifier):

        if 0 <= value:
            HeaterDurationCmdString = 'axis-cgi/param.cgi?action=update&TemperatureControl.Heater.H7.ManualControlDuration={}'.format(value)
            self.__SetHelper('HeaterDuration', value, qualifier, url=HeaterDurationCmdString)
        else:
            self.Discard('Invalid Command for SetHeaterDuration')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'            : 'up',
            'Down'          : 'down',
            'Left'          : 'left',
            'Right'         : 'right',
            'Up-Left'       : 'upleft',
            'Up-Right'      : 'upright',
            'Down-Left'     : 'downleft',
            'Down-Right'    : 'downright',
            'Stop'          : 'stop',
            'Home'          : 'home'
        }

        if value in ValueStateValues:
            PanTiltCmdString = 'axis-cgi/com/ptz.cgi?move={0}'.format(ValueStateValues[value])
            self.__SetHelper('PanTilt', value, qualifier, url=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltSpeed(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PanTiltSpeedCmdString = 'axis-cgi/com/ptz.cgi?speed={0}'.format(value)
            self.__SetHelper('PanTiltSpeed', value, qualifier, url=PanTiltSpeedCmdString)
        else:
            self.Discard('Invalid Command for SetPanTiltSpeed')

    def UpdatePanTiltSpeed(self, value, qualifier):

        PanTiltSpeedCmdString = 'axis-cgi/com/ptz.cgi?query=speed'
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
            PresetRecallCmdString = 'axis-cgi/com/ptz.cgi?gotoserverpresetno={0}'.format(value)
            self.__SetHelper('PresetRecall', value, qualifier, url=PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PresetSaveCmdString = 'axis-cgi/com/ptzconfig.cgi?setserverpresetno={0}'.format(value)
            self.__SetHelper('PresetSave', value, qualifier, url=PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetWiper(self, value, qualifier):

        ValueStateValues = ['Start', 'Stop']

        if value in ValueStateValues and 9 <= qualifier['Duration'] <= 900:
            WiperCmdString = 'axis-cgi/clearviewcontrol.cgi'
            data = {
                'apiVersion': '1.0',
                'context': 'my context',
                'method': value.lower(),
                'params': {
                    'id': 0
                }
            }

            if value == 'Start':
                data['params']['duration'] = qualifier['Duration']

            self.__SetHelper('Wiper', value, qualifier, url=WiperCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetWiper')

    def SetZoom(self, value, qualifier):

        if 1 <= value <= 9999:
            ZoomCmdString = 'axis-cgi/com/ptz.cgi?zoom={0}'.format(value)
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        if command == 'Wiper':
            headers = {'Content-Type': 'application/json'}
        else:
            headers = {'Content-Type': 'text/plain'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
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

        url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Content-Type': 'text/plain'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
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
                self.Subscription[command] = {'method':{}}
        
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
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
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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