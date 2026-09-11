from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack

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
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'BacklightCompensation': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Home': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = pack('B', 0x80 + int(value))
        else:
            self.Error(['Invalid Device ID parameter.'])

    def SetAutoFocus(self, value, qualifier):
        
        ValueStateValues = {
            'On' : 0x02, 
            'Off': 0x03
        }
        
        if value in ValueStateValues:
            AutoFocusCmdString = self._DeviceID + b'\x01\x04\x38' + bytes([ValueStateValues[value], 0xFF])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):
        
        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        AutoFocusCmdString = self._DeviceID + b'\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklightCompensation(self, value, qualifier):
        
        ValueStateValues = {
            'On' : 0x02, 
            'Off': 0x03
        }
        
        if value in ValueStateValues:
            BacklightCompensationCmdString = self._DeviceID + b'\x01\x04\x33' + bytes([ValueStateValues[value], 0xFF])
            self.__SetHelper('BacklightCompensation', BacklightCompensationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightCompensation')

    def UpdateBacklightCompensation(self, value, qualifier):
        
        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        BacklightCompensationCmdString = self._DeviceID + b'\x09\x04\x33\xFF'
        res = self.__UpdateHelper('BacklightCompensation', BacklightCompensationCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('BacklightCompensation', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight Compensation: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):
        
        focus_speed = int(qualifier['Speed'])
        
        ValueStateValues = {
            'Far' : 0x20 + focus_speed, 
            'Near': 0x30 + focus_speed, 
            'Stop': 0x00
        }
        
        if value in ValueStateValues and 0 <= focus_speed <= 7:
            FocusCmdString = self._DeviceID + b'\x01\x04\x08' + bytes([ValueStateValues[value], 0xFF])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetHome(self, value, qualifier):
        
        HomeCmdString = self._DeviceID + b'\x01\x06\x04\xFF'
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : [0x03, 0x01],
            'Down'       : [0x03, 0x02],
            'Left'       : [0x01, 0x03],
            'Right'      : [0x02, 0x03],
            'Up Left'    : [0x01, 0x01],
            'Up Right'   : [0x02, 0x01],
            'Down Left'  : [0x01, 0x02],
            'Down Right' : [0x02, 0x02],
            'Stop'       : [0x03, 0x03]
        }
        
        pan_speed, tilt_speed = int(qualifier['Pan Speed']), int(qualifier['Tilt Speed'])
        
        if value in ValueStateValues and 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 20:
            PanTiltCmdString = self._DeviceID + b'\x01\x06\x01' + bytes([pan_speed, tilt_speed] + ValueStateValues[value] + [0xFF])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):
        
        ValueStateValues = {
            'On' : 0x02, 
            'Off': 0x03
        }
        
        if value in ValueStateValues:
            PowerCmdString = self._DeviceID + b'\x01\x04\x00' + bytes([ValueStateValues[value], 0xFF])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
        
        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):
        
        ActionStates = {
            'Save'  : 0x01, 
            'Recall': 0x02
        }

        preset = int(value)
        if 1 <= preset <= 16 and qualifier['Action'] in ActionStates:
            PresetCmdString = self._DeviceID + b'\x01\x04\x3F' + bytes([ActionStates[qualifier['Action']], preset, 0xFF])
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetVideoMute(self, value, qualifier):
        
        ValueStateValues = {
            'On' : 0x02, 
            'Off': 0x03
        }
        
        if value in ValueStateValues:
            VideoMuteCmdString = self._DeviceID + b'\x01\x04\x75' + bytes([ValueStateValues[value], 0xFF])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):
        
        ValueStateValues = {
            0x02: 'On', 
            0x03: 'Off'
        }

        VideoMuteCmdString = self._DeviceID + b'\x09\x04\x75\xFF'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):
        
        zoom_speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Tele': 0x20 + zoom_speed, 
            'Wide': 0x30 + zoom_speed, 
            'Stop': 0x00
        }
        
        if value in ValueStateValues and 0 <= zoom_speed <= 7:
            ZoomCmdString = self._DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value], 0xFF])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'BacklightCompensation': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Home': { 'Status': {}},
            'Pan': {'Parameters': ['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Tilt': {'Parameters': ['Speed'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }   

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

            self.AddMatchString(re.compile(b'auto_focus:\s*(on|off)'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'backlight_compensation\s*(on|off)'), self.__MatchBacklightCompensation, None)
            self.AddMatchString(re.compile(b'\ngain\s*(\d+)\s'), self.__MatchGain, None)
            self.AddMatchString(re.compile(b'standby:\s*(on|off)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'mute:\s*(on|off)'), self.__MatchVideoMute, None)

    def __MatchLogin(self, value, qualifier):

        self.Send('admin\r\n')

    def __MatchPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n') 
    
    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   'auto',
            'Off':  'manual'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = 'camera focus mode {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = 'camera focus mode get\r\n'
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def __MatchAutoFocus(self, match, tag):

        ValueStateValues = {
            'on':   'On',
            'off':  'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoFocus', value, None)

    def SetBacklightCompensation(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            BacklightCompensationCmdString = 'camera ccu set backlight_compensation {}\r\n'.format(value.lower())
            self.__SetHelper('BacklightCompensation', BacklightCompensationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightCompensation')

    def UpdateBacklightCompensation(self, value, qualifier):

        BacklightCompensationCmdString = 'camera ccu get all\r\n'
        self.__UpdateHelper('BacklightCompensation', BacklightCompensationCmdString, value, qualifier)

    def __MatchBacklightCompensation(self, match, tag):

        ValueStateValues = {
            'on':   'On',
            'off':  'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BacklightCompensation', value, None)

    def SetFocus(self, value, qualifier):

        speed = qualifier['Speed']

        ValueStateValues = [
            'Far',
            'Near',
            'Stop'
        ]

        if 1 <= speed <= 8 and value in ValueStateValues:
            if value == 'Stop':
                FocusCmdString = 'camera focus stop\r\n'
            else:
                FocusCmdString = 'camera focus {} {}\r\n'.format(value.lower(), speed)

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        if 1 <= value <= 11:
            GainCmdString = 'camera ccu set gain {}\r\n'.format(value)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        self.UpdateBacklightCompensation(value, qualifier)

    def __MatchGain(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Gain', value, None)

    def SetHome(self, value, qualifier):

        HomeCmdString = 'camera home\r\n'
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPan(self, value, qualifier):

        speed = qualifier['Speed']

        ValueStateValues = [
            'Left',
            'Right',
            'Stop'
        ]

        if 1 <= speed <= 24 and value in ValueStateValues:
            if value == 'Stop':
                PanCmdString = 'camera pan stop\r\n'
            else:
                PanCmdString = 'camera pan {} {}\r\n'.format(value.lower(), speed)

            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'off',
            'Off':  'on'
        }

        if value in ValueStateValues:
            PowerCmdString = 'camera standby {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'camera standby get\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'off':  'On',
            'on':   'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save':     'store',
            'Recall':   'recall'
        }
        action = qualifier['Action']

        if action in ActionStates and 1 <= int(value) <= 16:
            if action == 'Save':
                PresetCmdString = 'camera preset {} {} save-ccu\r\n'.format(ActionStates[action], value)
            else:
                PresetCmdString = 'camera preset {} {}\r\n'.format(ActionStates[action], value)

            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTilt(self, value, qualifier):

        speed = qualifier['Speed']

        ValueStateValues = [
            'Up',
            'Down',
            'Stop'
        ]

        if 1 <= int(speed) <= 20 and value in ValueStateValues:
            if value == 'Stop':
                TiltCmdString = 'camera tilt stop\r\n'
            else:
                TiltCmdString = 'camera tilt {} {}\r\n'.format(value.lower(), speed)

            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            VideoMuteCmdString = 'video mute {}\r\n'.format(value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'video mute get\r\n'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            'on':   'On',
            'off':  'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetZoom(self, value, qualifier):

        speed = qualifier['Speed']

        ValueStateValues = [
            'In',
            'Out',
            'Stop'
        ]

        if 1 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                ZoomCmdString = 'camera zoom stop\r\n'
            else:
                ZoomCmdString = 'camera zoom {} {}\r\n'.format(value.lower(), speed)

            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)        

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
        
        #check incoming data if it matched any expected data from device module
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