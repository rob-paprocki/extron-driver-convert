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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Iris': {'Status': {}},
            'Mute': {'Status': {}},
            'PanTiltZoom': {'Parameters': ['Pan Speed', 'Tilt Speed', 'Zoom Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'WhiteBalance': {'Status': {}},
        }

        self._DeviceID = b'\x81'

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x88'
        else:
            self._DeviceID = bytes([int(value)+ 0x80])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x38\x02\xFF',
            'Off': b'\x01\x04\x38\x03\xFF'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        AutoFocusCmdString = self._DeviceID + b'\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x33\x02\xFF',
            'Off': b'\x01\x04\x33\x03\xFF'
        }

        if value in ValueStateValues:
            BacklightCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        BacklightCmdString = self._DeviceID + b'\x09\x04\x33\xFF'
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        focusSpeed = int(qualifier['Speed'])
        if value in ['Near', 'Far', 'Stop'] and 0 <= focusSpeed <= 7:
            FocusCmdString = ''

            if value == 'Near':
                FocusCmdString = self._DeviceID + b'\x01\x04\x08\x00' + bytes([0x30 + focusSpeed]) + b'\xFF'
            elif value == 'Far':
                FocusCmdString = self._DeviceID + b'\x01\x04\x08\x00' + bytes([0x20 + focusSpeed]) + b'\xFF'
            elif value == 'Stop':
                FocusCmdString = self._DeviceID + b'\x01\x04\x08\x00\xFF'

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x62\x02\xFF',
            'Off': b'\x01\x04\x62\x03\xFF'
        }

        if value in ValueStateValues:
            FreezeCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        FreezeCmdString = self._DeviceID + b'\x09\x04\x62\xFF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x0B\x00\xFF',
            'Up': b'\x01\x04\x0B\x02\xFF',
            'Down': b'\x01\x04\x0B\x03\xFF'
        }

        if value in ValueStateValues:
            IrisCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x75\x02\xFF',
            'Off': b'\x01\x04\x75\x03\xFF'
        }

        if value in ValueStateValues:
            MuteCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        MuteCmdString = self._DeviceID + b'\x09\x04\x75\xFF'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPanTiltZoom(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x03\x01\x03\xFF',
            'Down': b'\x03\x02\x03\xFF',
            'Left': b'\x01\x03\x03\xFF',
            'Right': b'\x02\x03\x03\xFF',
            'In': b'\x03\x03\x01\xFF',
            'Out': b'\x03\x03\x02\xFF',
            'Stop': b'\x03\x03\x03\xFF'
        }

        panSpeed = int(qualifier['Pan Speed'])
        tiltSpeed = int(qualifier['Tilt Speed'])
        zoomSpeed = int(qualifier['Zoom Speed'])
        PanTiltZoomCmdString = ''

        if value in ValueStateValues and 1 <= panSpeed <= 24 and 1 <= tiltSpeed <= 20 and 0 <= zoomSpeed <= 7:
            if value == 'Stop':
                PanTiltZoomCmdString = self._DeviceID + b'\x01\x06\x0A\x00\x00\x00' + ValueStateValues[value]
            else:
                PanTiltZoomCmdString = self._DeviceID + b'\x01\x06\x0A' + bytes([panSpeed, tiltSpeed, zoomSpeed]) + ValueStateValues[value]
            self.__SetHelper('PanTiltZoom', PanTiltZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltZoom')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        if value in ValueStateValues:
            PowerCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + bytes([int(value) - 1]) + b'\xFF'
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        ValueStateValues = {
            0: '1',
            1: '2',
            2: '3',
            3: '4',
            4: '5',
            5: '6',
            6: '7',
            7: '8',
            8: '9',
            9: '10',
            10: '11',
            11: '12',
            12: '13',
            13: '14',
            14: '15',
            15: '16'
        }

        PresetRecallCmdString = self._DeviceID + b'\x09\x04\x3F\xFF'
        res = self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('PresetRecall', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Preset Recall: Invalid/unexpected response'])

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = self._DeviceID + b'\x01\x04\x3F\x01' + bytes([int(value) - 1]) + b'\xFF'
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x04\x35\x00\xFF',
            'Indoor': b'\x01\x04\x35\x01\xFF',
            'Outdoor': b'\x01\x04\x35\x02\xFF',
            'One Push White Balance': b'\x01\x04\x35\x03\xFF',
            'ATW': b'\x01\x04\x35\x04\xFF',
            'Manual': b'\x01\x04\x35\x05\xFF',
            'One Push Trigger': b'\x01\x04\x10\x05\xFF',
            'Outdoor Auto': b'\x01\x04\x35\x06\xFF',
            'Sodium Lamp Auto': b'\x01\x04\x35\x07\xFF',
            'Sodium Lamp': b'\x01\x04\x35\x08\xFF',
            'Sodium Lamp Outdoor Auto': b'\x01\x04\x35\x09\xFF'
        }

        if value in ValueStateValues:
            WhiteBalanceCmdString = self._DeviceID + ValueStateValues[value]
            if value != 'One Push Trigger':
                self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Auto',
            0x01: 'Indoor',
            0x02: 'Outdoor',
            0x03: 'One Push White Balance',
            0x04: 'ATW',
            0x05: 'Manual',
            0x06: 'Outdoor Auto',
            0x07: 'Sodium Lamp Auto',
            0x08: 'Sodium Lamp',
            0x09: 'Sodium Lamp Outdoor Auto'
        }

        WhiteBalanceCmdString = self._DeviceID + b'\x09\x04\x35\xFF'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\x88':
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
        self._DeviceID = 1
        self.deviceUsername = 'admin'
        self.devicePassword = 'password'
        self.Models = {}



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'Firmware': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Pan': {'Parameters':['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Tilt': {'Parameters':['Speed'], 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

        self.Authenticated = False   
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'System Version:? +RoboSHOT [\S]+ (\d+\.\d+\.\d+)\r\n', re.I), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'ERROR'), self.__MatchError, None)

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
    
    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'camera focus mode auto\r\n',
            'Off' : 'camera focus mode manual\r\n'
        }
        
        if value in ValueStateValues:
            AutoFocusCmdString = ValueStateValues[value]
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')
            
    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'camera ccu set auto_iris on\r\n',
            'Off' : 'camera ccu set auto_iris off\r\n'
        }
        
        if value in ValueStateValues:
            AutoIrisCmdString = ValueStateValues[value]
            self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoIris')
            
    def UpdateFirmware(self, value, qualifier):


        FirmwareCmdString = 'version\r\n'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near'  : 'camera focus near ',
            'Far'   : 'camera focus far ',
            'Stop'  : 'camera focus stop\r\n'
        }

        focusSpeed = qualifier['Speed']

        if value in ValueStateValues and 1 <= int(focusSpeed) <= 8:
            if value == 'Stop':
                FocusCmdString = ValueStateValues[value]
            else:
                FocusCmdString = ValueStateValues[value] + focusSpeed + '\r\n'

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
            
    def SetPan(self, value, qualifier):

        ValueStateValues = {
            'Left'  : 'camera pan left',
            'Right' : 'camera pan right',
            'Stop'  : 'camera pan stop\r\n'
        }

        panSpeed = qualifier['Speed']
        PanCmdString = ''

        if value == 'Stop':
            PanCmdString = ValueStateValues[value]
        elif value == 'Left' or value == 'Right':
            if panSpeed == 'Default':
                PanCmdString = ValueStateValues[value] + '\r\n'
            elif 1 <= int(panSpeed) <= 24:
                PanCmdString = ValueStateValues[value] + ' ' + panSpeed + '\r\n'
            else:
                self.Discard('Invalid Command for SetPan')
        else:
            self.Discard('Invalid Command for SetPan')

        self.__SetHelper('Pan', PanCmdString, value, qualifier)
        
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'camera standby off\r\n',
            'Off' : 'camera standby on\r\n'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
            
    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = 'camera preset recall {}\r\n'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = 'camera preset store {}\r\n'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')
            
    def SetTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 'camera tilt up',
            'Down'  : 'camera tilt down',
            'Stop'  : 'camera tilt stop\r\n'
        }

        tiltSpeed = qualifier['Speed']
        TiltCmdString = ''

        if value == 'Stop':
            TiltCmdString = ValueStateValues[value]
        elif value == 'Up' or value == 'Down':
            if tiltSpeed == 'Default':
                TiltCmdString = ValueStateValues[value] + '\r\n'
            elif 1 <= int(tiltSpeed) <= 20:
                TiltCmdString = ValueStateValues[value] + ' ' + tiltSpeed + '\r\n'
            else:
                self.Discard('Invalid Command for SetTilt')
        else:
            self.Discard('Invalid Command for SetTilt')

        self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In'   : 'camera zoom in',
            'Out'  : 'camera zoom out',
            'Stop' : 'camera zoom stop\r\n'
        }

        zoomSpeed = qualifier['Speed']
        ZoomCmdString = ''

        if value == 'Stop':
            ZoomCmdString = ValueStateValues[value]
        elif value == 'In' or value == 'Out':
            if zoomSpeed == 'Default':
                ZoomCmdString = ValueStateValues[value] + '\r\n'
            elif 1 <= int(zoomSpeed) <= 7:
                ZoomCmdString = ValueStateValues[value] + ' ' + zoomSpeed + '\r\n'
            else:
                self.Discard('Invalid Command for SetZoom')
        else:
            self.Discard('Invalid Command for SetZoom')

        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Authenticated:
            self.Send(commandstring)
        else:
            print('Authentication failed')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)
        else:
            print('Authentication failed')

    def __MatchError(self, match, tag):
        self.counter = 0

        self.Error(["There was an error in the command response."])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = False
        
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
