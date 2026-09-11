from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Home': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'ResetPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }
        
        self._deviceID = 0x81

    @property
    def DeviceID(self):
        return self._deviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._deviceID = 0x80 + int(value)

    def SetAutoExposure(self, value, qualifier):

        state = {
            'Full Auto': 0x00,
            'Manual': 0x03
        }[value]

        AutoExposureCmdString = bytes([self._deviceID, 0x01, 0x04, 0x39, state, 0xFF])
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual'
        }

        AutoExposureCmdString = bytes([self._deviceID, 0x09, 0x04, 0x39, 0xFF])
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                print('AutoExposure: Invalid/Unexpected Response')

    def SetBacklightMode(self, value, qualifier):

        state = {
            'On': 0x02,
            'Off': 0x03
        }[value]

        BacklightModeCmdString = bytes([self._deviceID, 0x01, 0x04, 0x33, state, 0xFF])
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        BacklightModeCmdString = bytes([self._deviceID, 0x09, 0x04, 0x33, 0xFF])
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                print('BacklightMode: Invalid/Unexpected Response')

    def SetFocus(self, value, qualifier):

        focusSpd = int(qualifier['Focus Speed'])

        state = {
            'Near': 0x30 + focusSpd,
            'Far': 0x20 + focusSpd,
            'Stop': 0x00
        }[value]

        if 0 <= focusSpd <= 7:
            FocusCmdString = bytes([self._deviceID, 0x01, 0x04, 0x08, state, 0xFF])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        state = {
            'Auto': 0x02,
            'Manual': 0x03
        }[value]

        FocusModeCmdString = bytes([self._deviceID, 0x01, 0x04, 0x38, state, 0xFF])
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Auto',
            0x03: 'Manual'
        }

        FocusModeCmdString = bytes([self._deviceID, 0x09, 0x04, 0x38, 0xFF])
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                print('FocusMode: Invalid/Unexpected Response')

    def SetHome(self, value, qualifier):

        HomeCmdString = bytes([self._deviceID, 0x01, 0x06, 0x04, 0xFF])
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        state = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Up Left': b'\x01\x01',
            'Up Right': b'\x02\x01',
            'Down Left': b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop': b'\x03\x03'
        }[value]

        panSpd = int(qualifier['Pan Speed'])
        tiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= panSpd <= 24 and 1 <= tiltSpd <= 20:
            PanTiltCmdString = b''.join([bytes([self._deviceID, 0x01, 0x06, 0x01, panSpd, tiltSpd]), state, b'\xFF'])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        state = {
            'On': 0x02,
            'Off': 0x03
        }[value]

        PowerCmdString = bytes([self._deviceID, 0x01, 0x04, 0x00, state, 0xFF])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = bytes([self._deviceID, 0x09, 0x04, 0x00, 0xFF])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/Unexpected Response')

    def SetRecallPreset(self, value, qualifier):

        state = int(value) - 1
        if 0 <= state <= 15:
            RecallPresetCmdString = bytes([self._deviceID, 0x01, 0x04, 0x3F, 0x02, state, 0xFF])
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRecallPreset')

    def SetResetPreset(self, value, qualifier):

        state = int(value) - 1
        if 0 <= state <= 15:
            ResetPresetCmdString = bytes([self._deviceID, 0x01, 0x04, 0x3F, 0x00, state, 0xFF])
            self.__SetHelper('ResetPreset', ResetPresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetResetPreset')

    def SetSavePreset(self, value, qualifier):

        state = int(value) - 1
        if 0 <= state <= 15:
            SavePresetCmdString = bytes([self._deviceID, 0x01, 0x04, 0x3F, 0x01, state, 0xFF])
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSavePreset')

    def SetZoom(self, value, qualifier):

        zoomSpd = int(qualifier['Zoom Speed'])

        state = {
            'Tele': 0x20 + zoomSpd,
            'Wide': 0x30 + zoomSpd,
            'Stop': 0x00
        }[value]

        if 0 <= zoomSpd <= 7:
            ZoomCmdString = bytes([self._deviceID, 0x01, 0x04, 0x07, state, 0xFF])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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
            print(command, 'does not exist in the module')

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


class DeviceEthernetClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Home': {'Status': {}},
            'Pan': {'Parameters': ['Pan Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
            'Tilt': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
        }

        self.deviceUsername = 'admin'
        self.devicePassword = 'password'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'auto_focus:\s+(on|off)\r\n'), self.__MatchFocusMode, None)
            self.AddMatchString(re.compile(b'standby:\s+(on|off)\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'mute:\s+(on|off)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchSendUsername, None)
            self.AddMatchString(re.compile(b'\xFF\xFD\x01\xFF\xFD\x1F\xFF\xFB\x01\xFF\xFB\x03'), self.__MatchHandshake, None)
            self.AddMatchString(re.compile(b'ERROR'), self.__MatchError, None)

    def SetFocus(self, value, qualifier):

        focusSpd = int(qualifier['Focus Speed'])
        if 1 <= focusSpd <= 8 and value in ['Near', 'Far', 'Stop']:
            if value == 'Stop':
                FocusCmdString = 'camera focus stop\r\n'
            else:
                FocusCmdString = 'camera focus {0} {1}\r\n'.format(value.lower(), focusSpd)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        if value in ['Auto', 'Manual']:
            FocusModeCmdString = 'camera focus mode {0}\r\n'.format(value.lower())
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        FocusModeCmdString = 'camera focus mode get\r\n'
        self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def __MatchFocusMode(self, match, tag):

        value = {
            'on': 'Auto',
            'off': 'Manual'
        }[match.group(1).decode()]

        self.WriteStatus('FocusMode', value, None)

    def SetHome(self, value, qualifier):

        HomeCmdString = 'camera home\r\n'
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPan(self, value, qualifier):

        panSpd = int(qualifier['Pan Speed'])
        if 1 <= panSpd <= 24 and value in ['Left', 'Right', 'Stop']:
            if value == 'Stop':
                PanCmdString = 'camera pan stop\r\n'
            else:
                PanCmdString = 'camera pan {0} {1}\r\n'.format(value.lower(), panSpd)
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        powerVal = {
            'On': 'off',
            'Off': 'on'
        }[value]

        PowerCmdString = 'camera standby {0}\r\n'.format(powerVal)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'camera standby get\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = {
            'off': 'On',
            'on': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Power', value, None)

    def SetRecallPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetCmdString = 'camera preset recall {0}\r\n'.format(value)
            self.__SetHelper('RecallPreset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRecallPreset')

    def SetSavePreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            SavePresetCmdString = 'camera preset store {0}\r\n'.format(value)
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSavePreset')

    def SetTilt(self, value, qualifier):

        tiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= tiltSpd <= 20 and value in ['Up', 'Down', 'Stop']:
            if value == 'Stop':
                TiltCmdString = 'camera tilt stop\r\n'
            else:
                TiltCmdString = 'camera tilt {0} {1}\r\n'.format(value.lower(), tiltSpd)
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTilt')

    def SetVideoMute(self, value, qualifier):

        if value in ['On', 'Off']:
            VideoMuteCmdString = 'video mute {0}\r\n'.format(value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'video mute get\r\n'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('VideoMute', value, None)

    def SetZoom(self, value, qualifier):

        zoomSpd = int(qualifier['Zoom Speed'])
        if 1 <= zoomSpd <= 7 and value in ['In', 'Out', 'Stop']:
            if value == 'Stop':
                ZoomCmdString = 'camera zoom stop\r\n'
            else:
                ZoomCmdString = 'camera zoom {0} {1}\r\n'.format(value.lower(), zoomSpd)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __MatchHandshake(self, match, tag):
        self.__SetHelper('Handshake', b'\xFF\xFC\x01\xFF\xFC\x1F\xFF\xFE\x01\xFF\xFE\x03', None, None)

    def __MatchSendUsername(self, match, tag):

        self.Send(self.deviceUsername + '\r\n')
        self.Send(self.devicePassword + '\r\n')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        print('Error')

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
            print(command, 'does not exist in the module')

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

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}


   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
