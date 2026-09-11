from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Home': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            print('Invalid Device ID Parameter.')

    def __CommandBuilder(self, ctrl, len, cmd, data=[]):
        return bytes([self._DeviceID, ctrl, len, cmd] + data + [0xFF])

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Auto': 0x00,
            'Manual': 0x03
        }

        if value in ValueStateValues:
            self.__SetHelper('AutoExposure', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x39, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Auto',
            0x03: 'Manual'
        }

        res = self.__UpdateHelper('AutoExposure', self.__CommandBuilder(ctrl=0x09, len=0x04, cmd=0x39), value, qualifier)
        if res:
            try:
                self.WriteStatus('AutoExposure', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            self.__SetHelper('Backlight', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x33, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        res = self.__UpdateHelper('Backlight', self.__CommandBuilder(ctrl=0x09, len=0x04, cmd=0x33), value, qualifier)
        if res:
            try:
                self.WriteStatus('Backlight', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        focus_speed = int(qualifier['Focus Speed'])

        ValueStateValues = {
            'Far': 0x20 + focus_speed,
            'Near': 0x30 + focus_speed,
            'Stop': 0x00
        }

        if value in ValueStateValues and 0 <= focus_speed <= 7:
            self.__SetHelper('Focus', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x08, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 0x02,
            'Manual': 0x03
        }

        if value in ValueStateValues:
            self.__SetHelper('FocusMode', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x38, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Auto',
            0x03: 'Manual'
        }

        res = self.__UpdateHelper('FocusMode', self.__CommandBuilder(ctrl=0x09, len=0x04, cmd=0x38), value, qualifier)
        if res:
            try:
                self.WriteStatus('FocusMode', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetHome(self, value, qualifier):

        self.__SetHelper('Home', self.__CommandBuilder(ctrl=0x01, len=0x06, cmd=0x04), value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            self.__SetHelper('Iris', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x0B, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03]
        }

        pan_speed, tilt_speed = int(qualifier['Pan Speed']), int(qualifier['Tilt Speed'])

        if value in ValueStateValues and 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 20:
            self.__SetHelper('PanTilt', self.__CommandBuilder(ctrl=0x01, len=0x06, cmd=0x01, data=[pan_speed, tilt_speed] + ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x00, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off',
            0x04: 'Internal Power Circuit Error'
        }

        res = self.__UpdateHelper('Power', self.__CommandBuilder(ctrl=0x09, len=0x04, cmd=0x00), value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('PresetRecall', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x3F, data=[0x02, int(value) - 1]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('PresetReset', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x3F, data=[0x00, int(value) - 1]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('PresetSave', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x3F, data=[0x01, int(value) - 1]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            self.__SetHelper('Shutter', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x0A, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            self.__SetHelper('VideoMute', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x75, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        res = self.__UpdateHelper('VideoMute', self.__CommandBuilder(ctrl=0x09, len=0x04, cmd=0x75), value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['VideoMute: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        zoom_speed = int(qualifier['Zoom Speed'])

        ValueStateValues = {
            'Tele': 0x20 + zoom_speed,
            'Wide': 0x30 + zoom_speed,
            'Stop': 0x00
        }

        if value in ValueStateValues and 0 <= zoom_speed <= 7:
            self.__SetHelper('Zoom', self.__CommandBuilder(ctrl=0x01, len=0x04, cmd=0x07, data=[ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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


class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'admin'
        self.devicePassword = 'password'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Home': { 'Status': {}},
            'Pan': {'Parameters': ['Pan Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Tilt': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

        self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'backlight_compensation\s+?(on|off)'), self.__MatchBacklight, None)
            self.AddMatchString(re.compile(b'auto_focus:\s+?(on|off)'), self.__MatchFocusMode, None)
            self.AddMatchString(re.compile(b'standby:\s+?(on|off)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'login:', re.I), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'password:', re.I), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Welcome', re.I), self.__MatchAuthenticated, None)

    def SetSendPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n')

    def SetSendUsername(self, value, qualifier):

        self.Send(self.deviceUsername + '\r\n')

    def __MatchUsername(self, match, tag):

        self.SetSendUsername( None, None)

    def __MatchPassword(self, match, tag):

        self.SetSendPassword( None, None)

    def __MatchAuthenticated(self, match, tag):

        self.Authenticated = True

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on',
            'Off': 'off'
        }

        if value in ValueStateValues:
            self.__SetHelper('Backlight', 'camera ccu set backlight_compensation {}\r\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        self.__UpdateHelper('Backlight', 'camera ccu get backlight_compensation\r\n', value, qualifier)

    def __MatchBacklight(self, match, tag):

        ValueStateValues = {
            'on' : 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Backlight', value, None)

    def SetFocus(self, value, qualifier):

        focus_speed = int(qualifier['Focus Speed'])

        ValueStateValues = {
            'Near': 'near {}'.format(focus_speed),
            'Far' : 'far {}'.format(focus_speed),
            'Stop': 'stop'
        }

        if value in ValueStateValues and 1 <= focus_speed <= 8:
            self.__SetHelper('Focus', 'camera focus {}\r\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'  : 'auto',
            'Manual': 'manual'
        }

        if value in ValueStateValues:
            self.__SetHelper('FocusMode', 'camera focus mode {}\r\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        self.__UpdateHelper('FocusMode', 'camera focus mode get\r\n', value, qualifier)

    def __MatchFocusMode(self, match, tag):

        ValueStateValues = {
            'on' : 'Auto',
            'off': 'Manual'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FocusMode', value, None)

    def SetHome(self, value, qualifier):

        self.__SetHelper('Home', 'camera home\r\n', value, qualifier)

    def SetPan(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])

        ValueStateValues = {
            'Left' : 'left {}'.format(pan_speed),
            'Right': 'right {}'.format(pan_speed),
            'Stop' : 'stop'
        }

        if value in ValueStateValues and 1 <= pan_speed <= 24:
            self.__SetHelper('Pan', 'camera pan {}\r\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'off',
            'Off': 'on'
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', 'camera standby {}\r\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'camera standby get\r\n', value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'off': 'On',
            'on' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('PresetRecall', 'camera preset recall {}\r\n'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('PresetSave', 'camera preset store {}\r\n'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetTilt(self, value, qualifier):

        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up'  : 'up {}'.format(tilt_speed),
            'Down': 'down {}'.format(tilt_speed),
            'Stop': 'stop'
        }

        if value in ValueStateValues and 1 <= tilt_speed <= 20:
            self.__SetHelper('Tilt', 'camera tilt {}\r\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetZoom(self, value, qualifier):

        zoom_speed = int(qualifier['Zoom Speed'])

        ValueStateValues = {
            'In'  : 'in {}'.format(zoom_speed),
            'Out' : 'out {}'.format(zoom_speed),
            'Stop': 'stop'
        }

        if value in ValueStateValues and 1 <= zoom_speed <= 7:
            self.__SetHelper('Zoom', 'camera zoom {}\r\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Authenticated:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.Authenticated:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                    self.Send(commandstring)
            else:
                self.Error(['Device not authenticated.'])

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()