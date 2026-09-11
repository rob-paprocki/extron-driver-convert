# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack
import re

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
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Iris': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PanTiltZoom': {'Parameters':['Pan Speed','Tilt Speed','Zoom Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'RecallTriSync': { 'Status': {}},
            'SetTriSync': {'Parameters':['Speed'], 'Status': {}},
            'WhiteBalance': { 'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        DeviceIDMatch = {
            '1' : b'\x81',
            '2' : b'\x82',
            '3' : b'\x83',
            '4' : b'\x84',
            '5' : b'\x85',
            '6' : b'\x86',
            '7' : b'\x87'
        }

        if value in DeviceIDMatch:
            self._DeviceID = DeviceIDMatch[value]
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'     : b'\x01\x04\x38\x02\xFF', 
            'Off'    : b'\x01\x04\x38\x03\xFF'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }

        AutoFocusCmdString = self._DeviceID + b'\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x01\x04\x33\x02\xFF', 
            'Off'   : b'\x01\x04\x33\x03\xFF'
        }

        if value in ValueStateValues:
            BacklightCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On',
            b'\x03' : 'Off'
        }

        BacklightCmdString = self._DeviceID + b'\x09\x04\x33\xFF'
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near'      : 0x30, 
            'Far'       : 0x20, 
            'Stop'      : b'\x01\x04\x08\x00\xFF'
        }

        if value in ValueStateValues and 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                FocusCmdString = self._DeviceID + ValueStateValues[value]
            else:
                FocusCmdString = self._DeviceID + b'\x01\x04\x08' + pack('>B', ValueStateValues[value] + int(qualifier['Speed'])) + b'\xFF'

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01\x04\x62\x02\xFF',
            'Off' : b'\x01\x04\x62\x03\xFF'
        }

        if value in ValueStateValues:
            FreezeCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On',
            b'\x03' : 'Off'
        }

        FreezeCmdString = self._DeviceID +  b'\x09\x04\x62\xFF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset'     : b'\x01\x04\x0B\x00\xFF', 
            'Up'        : b'\x01\x04\x0B\x02\xFF', 
            'Down'      : b'\x01\x04\x0B\x03\xFF'
        }

        if value in ValueStateValues:
            IrisCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x01\x04\x75\x02\xFF', 
            'Off'   : b'\x01\x04\x75\x03\xFF'
        }

        if value in ValueStateValues:
            MuteCmdString = self._DeviceID +  ValueStateValues[value]
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        MuteCmdString = self._DeviceID + b'\x09\x04\x75\xFF'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPanTiltZoom(self, value, qualifier):

        PanSpeedStates = {
            '1'  : b'\x01',
            '2'  : b'\x02', 
            '3'  : b'\x03', 
            '4'  : b'\x04', 
            '5'  : b'\x05', 
            '6'  : b'\x06', 
            '7'  : b'\x07', 
            '8'  : b'\x08', 
            '9'  : b'\x09', 
            '10' : b'\x0A', 
            '11' : b'\x0B', 
            '12' : b'\x0C', 
            '13' : b'\x0D', 
            '14' : b'\x0E', 
            '15' : b'\x0F', 
            '16' : b'\x10', 
            '17' : b'\x11', 
            '18' : b'\x12', 
            '19' : b'\x13', 
            '20' : b'\x14', 
            '21' : b'\x15', 
            '22' : b'\x16', 
            '23' : b'\x17', 
            '24' : b'\x18'
        }

        TiltSpeedStates = {
            '1'  : b'\x01', 
            '2'  : b'\x02', 
            '3'  : b'\x03', 
            '4'  : b'\x04', 
            '5'  : b'\x05', 
            '6'  : b'\x06', 
            '7'  : b'\x07', 
            '8'  : b'\x08', 
            '9'  : b'\x09', 
            '10' : b'\x0A', 
            '11' : b'\x0B', 
            '12' : b'\x0C', 
            '13' : b'\x0D', 
            '14' : b'\x0E', 
            '15' : b'\x0F', 
            '16' : b'\x10', 
            '17' : b'\x11', 
            '18' : b'\x12', 
            '19' : b'\x13', 
            '20' : b'\x14'
        }

        ZoomSpeedStates = {
            '0'  : b'\x00',
            '1'  : b'\x01', 
            '2'  : b'\x02', 
            '3'  : b'\x03', 
            '4'  : b'\x04', 
            '5'  : b'\x05', 
            '6'  : b'\x06', 
            '7'  : b'\x07'
        }

        ValueStateValues = {
            'Up'         : b'\x03\x01\x03\xFF',
            'Down'       : b'\x03\x02\x03\xFF',
            'Left'       : b'\x01\x03\x03\xFF',
            'Right'      : b'\x02\x03\x03\xFF',
            'Up Left'    : b'\x01\x01\xFF',
            'Up Right'   : b'\x02\x01\xFF',
            'Down Left'  : b'\x01\x02\xFF',
            'Down Right' : b'\x02\x02\xFF',
            'In'         : b'\x03\x03\x01\xFF',
            'Out'        : b'\x03\x03\x02\xFF',
            'Stop'       : b'\x03\x03\x03\xFF'
        }

        if value in ValueStateValues and qualifier['Pan Speed'] in PanSpeedStates and qualifier['Tilt Speed'] in TiltSpeedStates and qualifier['Zoom Speed'] in ZoomSpeedStates:
            if value in ['Up Left', 'Up Right', 'Down Left', 'Down Right']:
                PanTiltZoomCmdString = self._DeviceID + b'\x01\x06\x0A' + PanSpeedStates[qualifier['Pan Speed']] + TiltSpeedStates[qualifier['Tilt Speed']] + ValueStateValues[value]
            else:
                PanTiltZoomCmdString = self._DeviceID + b'\x01\x06\x0A' + PanSpeedStates[qualifier['Pan Speed']] + TiltSpeedStates[qualifier['Tilt Speed']] + ZoomSpeedStates[qualifier['Zoom Speed']] + ValueStateValues[value]
            self.__SetHelper('PanTiltZoom', PanTiltZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltZoom')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01\x04\x00\x02\xFF',
            'Off' : b'\x01\x04\x00\x03\xFF'
        }

        if value in ValueStateValues:
            PowerCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
    
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1'  : b'\x00',
            '2'  : b'\x01',
            '3'  : b'\x02',
            '4'  : b'\x03',
            '5'  : b'\x04',
            '6'  : b'\x05',
            '7'  : b'\x06',
            '8'  : b'\x07',
            '9'  : b'\x08',
            '10' : b'\x09', 
            '11' : b'\x0A', 
            '12' : b'\x0B', 
            '13' : b'\x0C', 
            '14' : b'\x0D', 
            '15' : b'\x0E', 
            '16' : b'\x0F'
        }

        if value in ValueStateValues:
            PresetRecallCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1'  : b'\x00',
            '2'  : b'\x01',
            '3'  : b'\x02',
            '4'  : b'\x03',
            '5'  : b'\x04',
            '6'  : b'\x05',
            '7'  : b'\x06',
            '8'  : b'\x07',
            '9'  : b'\x08',
            '10' : b'\x09', 
            '11' : b'\x0A', 
            '12' : b'\x0B', 
            '13' : b'\x0C', 
            '14' : b'\x0D', 
            '15' : b'\x0E', 
            '16' : b'\x0F'
        }

        if value in ValueStateValues:
            PresetSaveCmdString = self._DeviceID + b'\x01\x04\x3F\x01' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRecallTriSync(self, value, qualifier):

        ValueStateValues = {
            '0'  : 0x00,
            '1'  : 0x01,
            '2'  : 0x02,
            '3'  : 0x03,
            '4'  : 0x04,
            '5'  : 0x05,
            '6'  : 0x06,
            '7'  : 0x07,
            '8'  : 0x08,
            '9'  : 0x09,
            '10' : 0x0A, 
            '11' : 0x0B, 
            '12' : 0x0C, 
            '13' : 0x0D, 
            '14' : 0x0E, 
            '15' : 0x0F
        }

        if value in ValueStateValues:
            RecallTriSyncCmdString = self._DeviceID + pack('>BBBBBB',  0x01, 0x04, 0x3F, 0x12, ValueStateValues[value], 0xFF)
            self.__SetHelper('RecallTriSync', RecallTriSyncCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallTriSync')

    def SetSetTriSync(self, value, qualifier):

        ValueStateValues = {
            '0'  : 0x00,
            '1'  : 0x01,
            '2'  : 0x02,
            '3'  : 0x03,
            '4'  : 0x04,
            '5'  : 0x05,
            '6'  : 0x06,
            '7'  : 0x07,
            '8'  : 0x08,
            '9'  : 0x09,
            '10' : 0x0A, 
            '11' : 0x0B, 
            '12' : 0x0C, 
            '13' : 0x0D, 
            '14' : 0x0E, 
            '15' : 0x0F
        }

        if value in ValueStateValues and 1 <= int(qualifier['Speed']) <= 26:
            speed = int(qualifier['Speed'])
            byte1 = speed // 16
            byte2 = speed % 16 
            SetTriSyncCmdString = self._DeviceID + pack('>BBBBBBBB', 0x01, 0x04, 0x3F, 0x31, ValueStateValues[value],byte1,byte2,0xFF) 
            self.__SetHelper('SetTriSync', SetTriSyncCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetTriSync')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto'                      : b'\x01\x04\x35\x00\xFF', 
            'Indoor'                    : b'\x01\x04\x35\x01\xFF', 
            'Outdoor'                   : b'\x01\x04\x35\x02\xFF', 
            'One Push White Balance'    : b'\x01\x04\x35\x03\xFF', 
            'ATW'                       : b'\x01\x04\x35\x04\xFF', 
            'Manual'                    : b'\x01\x04\x35\x05\xFF', 
            'One Push Trigger'          : b'\x01\x04\x10\x05\xFF', 
            'Outdoor Auto'              : b'\x01\x04\x35\x06\xFF', 
            'Sodium Lamp Auto'          : b'\x01\x04\x35\x07\xFF', 
            'Sodium Lamp'               : b'\x01\x04\x35\x08\xFF', 
            'Sodium Lamp Outdoor Auto'  : b'\x01\x04\x35\x09\xFF'
        }

        if value in ValueStateValues:
            WhiteBalanceCmdString = self._DeviceID + ValueStateValues[value]
            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Auto',
            b'\x01': 'Indoor',
            b'\x02': 'Outdoor',
            b'\x03': 'One Push White Balance',
            b'\x04': 'ATW',
            b'\x05': 'Manual',
            b'\x06': 'Outdoor Auto',
            b'\x07': 'Sodium Lamp Auto',
            b'\x08': 'Sodium Lamp',
            b'\x09': 'Sodium Lamp Outdoor Auto'
        }

        WhiteBalanceCmdString = self._DeviceID + b'\x09\x04\x35\xFF'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag= b'\xFF')
            if not res:
                self.Error(['Unexpected/Invalid response'])
            else:
                res = res

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
        self.deviceUsername = 'admin'
        self.devicePassword = 'password'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'Pan': {'Parameters':['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Tilt': {'Parameters':['Speed'], 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'auto_focus:\s*(on|off)'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'auto_iris\s+(on|off)\r\n'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'iris\s+([0-9]|1[0-3])\r\n'), self.__MatchIris, None)
            self.AddMatchString(re.compile(b'standby:\s+(on|off)\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ERROR'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'\xFF\xFD\x01\xFF\xFD\x1F\xFF\xFB\x01\xFF\xFB\x03'), self.__MatchHandshake, None)

    def SetHandshake(self, value, qualifier):

        self.__SetHelper('Handshake', b'\xFF\xFC\x01\xFF\xFC\x1F\xFF\xFE\x01\xFF\xFE\x03', None, None)

    def __MatchHandshake(self, match, tag):

        self.SetHandshake( None, None)

    def SetSendPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n')

    def SetSendUsername(self, value, qualifier):

        self.Send(self.deviceUsername + '\r\n')

    def __MatchUsername(self, match, tag):

        self.SetSendUsername( None, None)

    def __MatchPassword(self, match, tag):

        self.SetSendPassword( None, None)
        
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

    def UpdateAutoIris(self, value, qualifier):

        AutoIrisCmdString = 'camera ccu get auto_iris\r\n'
        self.__UpdateHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def __MatchAutoIris(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutoIris', value, None)

    def SetFocus(self, value, qualifier):

        FocusSpeedStates = {
            '0' : ' 1\r\n',
            '1' : ' 2\r\n',
            '2' : ' 3\r\n',
            '3' : ' 4\r\n',
            '4' : ' 5\r\n',
            '5' : ' 6\r\n',
            '6' : ' 7\r\n',
            '7' : ' 8\r\n'
        }

        ValueStateValues = {
            'Near' : 'camera focus near', 
            'Far'  : 'camera focus far',
            'Stop' : 'camera focus stop\r\n'
        }

        if value in ValueStateValues and qualifier['Speed'] in FocusSpeedStates:
            if value in ['Stop']:
                FocusCmdString = ValueStateValues[value]
            else:
                FocusCmdString = ValueStateValues[value] + FocusSpeedStates[qualifier['Speed']]

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        if 0 <= value <= 13:
            IrisCmdString = 'camera ccu set iris {}\r\n'.format(value)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = 'camera ccu get iris\r\n'
        self.__UpdateHelper('AutoIris', IrisCmdString, value, qualifier)

    def __MatchIris(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Iris', value, None)

    def SetPan(self, value, qualifier):

        SpeedStates = {
            'Default' : '\r\n', 
            '1'  : ' 1\r\n',
            '2'  : ' 2\r\n',
            '3'  : ' 3\r\n',
            '4'  : ' 4\r\n',
            '5'  : ' 5\r\n',
            '6'  : ' 6\r\n',
            '7'  : ' 7\r\n',
            '8'  : ' 8\r\n',
            '9'  : ' 9\r\n',
            '10' : ' 10\r\n', 
            '11' : ' 11\r\n', 
            '12' : ' 12\r\n', 
            '13' : ' 13\r\n', 
            '14' : ' 14\r\n', 
            '15' : ' 15\r\n', 
            '16' : ' 16\r\n', 
            '17' : ' 17\r\n', 
            '18' : ' 18\r\n', 
            '19' : ' 19\r\n', 
            '20' : ' 20\r\n', 
            '21' : ' 21\r\n', 
            '22' : ' 22\r\n', 
            '23' : ' 23\r\n', 
            '24' : ' 24\r\n'
        }

        ValueStateValues = {
            'Left'  : 'camera pan left',
            'Right' : 'camera pan right', 
            'Stop'  : 'camera pan stop\r\n'
        }

        if value in ValueStateValues and qualifier['Speed'] in SpeedStates:
            if value == 'Stop':
                PanCmdString = ValueStateValues[value]
            else:
                PanCmdString = ValueStateValues[value] + SpeedStates[qualifier['Speed']]

            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'system standby off\r\n',
            'Off' : 'system standby on\r\n'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'system standby get\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'off' : 'On',
            'on'  : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = 'camera preset recall {0}\r\n'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = 'camera preset store {0}\r\n'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetTilt(self, value, qualifier):

        SpeedStates = {
            'Default' : '\r\n', 
            '1'  : ' 1\r\n',
            '2'  : ' 2\r\n',
            '3'  : ' 3\r\n',
            '4'  : ' 4\r\n',
            '5'  : ' 5\r\n',
            '6'  : ' 6\r\n',
            '7'  : ' 7\r\n',
            '8'  : ' 8\r\n',
            '9'  : ' 9\r\n',
            '10' : ' 10\r\n', 
            '11' : ' 11\r\n', 
            '12' : ' 12\r\n', 
            '13' : ' 13\r\n', 
            '14' : ' 14\r\n', 
            '15' : ' 15\r\n', 
            '16' : ' 16\r\n', 
            '17' : ' 17\r\n', 
            '18' : ' 18\r\n', 
            '19' : ' 19\r\n', 
            '20' : ' 20\r\n'
        }

        ValueStateValues = {
            'Up'   : 'camera tilt up',
            'Down' : 'camera tilt down', 
            'Stop' : 'camera tilt stop\r\n'
        }

        if value in ValueStateValues and qualifier['Speed'] in SpeedStates:
            if value == 'Stop':
                TiltCmdString = ValueStateValues[value]
            else:
                TiltCmdString = ValueStateValues[value] + SpeedStates[qualifier['Speed']]
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetZoom(self, value, qualifier):

        SpeedStates = {
            'Default' : '\r\n', 
            '1' : ' 1\r\n', 
            '2' : ' 2\r\n', 
            '3' : ' 3\r\n', 
            '4' : ' 4\r\n', 
            '5' : ' 5\r\n', 
            '6' : ' 6\r\n', 
            '7' : ' 7\r\n'
        }

        ValueStateValues = {
            'In'   : 'camera zoom in',
            'Out'  : 'camera zoom out',
            'Stop' : 'camera zoom stop\r\n'
        }

        if value in ValueStateValues and qualifier['Speed'] in SpeedStates:
            if value == 'Stop':
                ZoomCmdString = ValueStateValues[value]
            else:
                ZoomCmdString = ValueStateValues[value] + SpeedStates[qualifier['Speed']]

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()