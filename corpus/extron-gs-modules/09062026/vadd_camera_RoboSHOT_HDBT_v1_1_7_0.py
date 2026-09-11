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
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PanTiltZoom': {'Parameters': ['Pan Speed', 'Tilt Speed', 'Zoom Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': {'Parameters': ['Type'], 'Status': {}},
            'PresetTriSyncSave': {'Parameters': ['Speed'], 'Status': {}},
            'WhiteBalance': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0x88
        elif 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01\x04\x38\x02\xFF', 
            'Off':  b'\x01\x04\x38\x03\xFF'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On', 
            0x03: 'Off'
        }

        AutoFocusCmdString = pack('>B4s', self._DeviceID, b'\x09\x04\x38\xFF')
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AutoFocus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01\x04\x33\x02\xFF', 
            'Off':  b'\x01\x04\x33\x03\xFF'
        }

        if value in ValueStateValues:
            BacklightCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On', 
            0x03: 'Off'
        }

        BacklightCmdString = pack('>B4s', self._DeviceID, b'\x09\x04\x33\xFF')
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far':  0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        if value in ValueStateValues and 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                FocusCmdString = pack('>B5s', self._DeviceID, b'\x01\x04\x08\x00\xFF')
            else:
                FocusCmdString = pack('>B3sBB', self._DeviceID, b'\x01\x04\x08', int(qualifier['Speed']) + ValueStateValues[value], 0xFF)

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01\x04\x62\x02\xFF', 
            'Off':  b'\x01\x04\x62\x03\xFF'
        }

        if value in ValueStateValues:
            FreezeCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On', 
            0x03: 'Off'
        }

        FreezeCmdString = pack('>B4s', self._DeviceID, b'\x09\x04\x62\xFF')
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Reset':    b'\x01\x04\x0C\x00\xFF', 
            'Up':       b'\x01\x04\x0C\x02\xFF', 
            'Down':     b'\x01\x04\x0C\x03\xFF'
        }

        if value in ValueStateValues:
            GainCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset':    b'\x01\x04\x0B\x00\xFF', 
            'Up':       b'\x01\x04\x0B\x02\xFF', 
            'Down':     b'\x01\x04\x0B\x03\xFF'
        }

        if value in ValueStateValues:
            IrisCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01\x04\x75\x02\xFF', 
            'Off':  b'\x01\x04\x75\x03\xFF'
        }

        if value in ValueStateValues:
            MuteCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On', 
            0x03: 'Off'
        }

        MuteCmdString = pack('>B4s', self._DeviceID, b'\x09\x04\x75\xFF')
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPanTiltZoom(self, value, qualifier):

        ValueStateValues = {
            'Up':           b'\x03\x01\x03\xFF', 
            'Down':         b'\x03\x02\x03\xFF', 
            'Left':         b'\x01\x03\x03\xFF', 
            'Right':        b'\x02\x03\x03\xFF', 
            'In':           b'\x03\x03\x01\xFF', 
            'Out':          b'\x03\x03\x02\xFF', 
            'Stop':         b'\x03\x03\x03\xFF',
            'Home':         b'',
            'Up Left':      b'\x01\x01\xFF',
            'Up Right':     b'\x02\x01\xFF',
            'Down Left':    b'\x01\x02\xFF',
            'Down Right':   b'\x02\x02\xFF'
        }

        if all([value in ValueStateValues,
                1 <= int(qualifier['Pan Speed']) <= 24,
                1 <= int(qualifier['Tilt Speed']) <= 20,
                0 <= int(qualifier['Zoom Speed']) <= 7]):
            if value == 'Home':
                PanTiltZoomCmdString = pack('>B5s', self._DeviceID, b'\x01\x06\x0C\xFF')
            elif value in ['Up Left', 'Up Right', 'Down Left', 'Down Right']:
                PanTiltZoomCmdString = pack('B3sBB3s', self._DeviceID, b'\x01\x06\x01', int(qualifier['Pan Speed']), int(qualifier['Tilt Speed']), ValueStateValues[value])
            else:
                PanTiltZoomCmdString = pack('>B3sBBB4s', self._DeviceID, b'\x01\x06\x0A', int(qualifier['Pan Speed']), int(qualifier['Tilt Speed']), int(qualifier['Zoom Speed']), ValueStateValues[value])
            self.__SetHelper('PanTiltZoom', PanTiltZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltZoom')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01\x04\x00\x02\xFF', 
            'Off' : b'\x01\x04\x00\x03\xFF'
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        PowerCmdString = pack('>B4s', self._DeviceID, b'\x09\x04\x00\xFF')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = pack('>B4sBs', self._DeviceID, b'\x01\x04\x3F\x02', int(value) - 1, b'\xFF')
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        TypeStates = {
            'Standard'          : b'\x01',
            'Standard w/ Scene' : b'\x21'
        }

        if 1 <= int(value) <= 16 and qualifier['Type'] in TypeStates:
            PresetSaveCmdString = pack('>B3ssBs', self._DeviceID, b'\x01\x04\x3F', TypeStates[qualifier['Type']], int(value) - 1, b'\xFF')
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetPresetTriSyncSave(self, value, qualifier):

        if 1 <= int(value) <= 16 and 1 <= int(qualifier['Speed']) <= 24:
            speed = int(qualifier['Speed'])
            byte1 = speed // 16
            byte2 = speed % 16
            PresetTriSyncSaveCmdString = pack('>9B', self._DeviceID, 0x01, 0x04, 0x3F, 0x11, int(value) - 1, byte1, byte2, 0xFF)
            self.__SetHelper('PresetTriSyncSave', PresetTriSyncSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetTriSyncSave')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto'                     : b'\x01\x04\x35\x00\xFF', 
            'Indoor'                   : b'\x01\x04\x35\x01\xFF', 
            'Outdoor'                  : b'\x01\x04\x35\x02\xFF', 
            'One Push White Balance'   : b'\x01\x04\x35\x03\xFF', 
            'ATW'                      : b'\x01\x04\x35\x04\xFF', 
            'Manual'                   : b'\x01\x04\x35\x05\xFF', 
            'One Push Trigger'         : b'\x01\x04\x10\x05\xFF', 
            'Outdoor Auto'             : b'\x01\x04\x35\x06\xFF', 
            'Sodium Lamp Auto'         : b'\x01\x04\x35\x07\xFF', 
            'Sodium Lamp'              : b'\x01\x04\x35\x08\xFF', 
            'Sodium Lamp Outdoor Auto' : b'\x01\x04\x35\x09\xFF'
        }

        if value in ValueStateValues:
            WhiteBalanceCmdString = pack('>B5s', self._DeviceID, ValueStateValues[value])
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

        WhiteBalanceCmdString = pack('>B4s', self._DeviceID, b'\x09\x04\x35\xFF')
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['WhiteBalance: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0x88:
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
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'Pan': {'Parameters': ['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'PresetTriSyncSave': {'Parameters': ['Speed'], 'Status': {}},
            'Tilt': {'Parameters': ['Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchSendUsername, None)
            self.AddMatchString(re.compile(b'\r\nauto_focus: +(on|off)\r\n'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'\r\nauto_iris +(on|off)\r\n'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'backlight_compensation +(on|off)'), self.__MatchBacklight, None)
            self.AddMatchString(re.compile(b'\r\ngain +(\d+)\r\n'), self.__MatchGain, None)
            self.AddMatchString(re.compile(b'\r\niris +(\d+)\r\n'), self.__MatchIris, None)
            self.AddMatchString(re.compile(b'standby: +(on|off)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ERROR'), self.__MatchError, None)

    def SetSendPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n')

    def SetSendUsername(self, value, qualifier):
  
        self.Send(self.deviceUsername + '\r\n')

    def __MatchSendUsername(self, match, tag):

        self.SetSendUsername(None, None)
        self.SetSendPassword(None, None)
    
    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   'camera focus mode auto\r\n', 
            'Off':  'camera focus mode manual\r\n'
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

        value = match.group(1).decode().title()
        self.WriteStatus('AutoFocus', value, None)

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On':   'camera ccu set auto_iris on\r\n', 
            'Off':  'camera ccu set auto_iris off\r\n'
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

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   'camera ccu set backlight_compensation on\r\n',
            'Off':  'camera ccu set backlight_compensation off\r\n'
        }

        if value in ValueStateValues:
            BacklightCmdString = ValueStateValues[value]
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        BacklightCmdString = 'camera ccu get backlight_compensation\r\n'
        self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)

    def __MatchBacklight(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Backlight', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': 'camera focus near ',
            'Far':  'camera focus far ',
            'Stop': 'camera focus stop\r\n'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Speed']) <= 8:
            if value == 'Stop':
                FocusCmdString = ValueStateValues[value]
            else:
                FocusCmdString = ValueStateValues[value] + qualifier['Speed'] + '\r\n'

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        if 0 <= value <= 11:
            GainCmdString = 'camera ccu set gain {}\r\n'.format(value)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        GainCmdString = 'camera ccu get gain\r\n'
        self.__UpdateHelper('Gain', GainCmdString, value, qualifier)

    def __MatchGain(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 11:
            self.WriteStatus('Gain', value, None)

    def SetIris(self, value, qualifier):

        if 0 <= value <= 21:
            IrisCmdString = 'camera ccu set iris {}\r\n'.format(value)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = 'camera ccu get iris\r\n'
        self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)

    def __MatchIris(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 21:
            self.WriteStatus('Iris', value, None)

    def SetPan(self, value, qualifier):

        PanSpeedStates = {
            'Default':  '\r\n', 
            '1':        ' 1\r\n', 
            '2':        ' 2\r\n', 
            '3':        ' 3\r\n', 
            '4':        ' 4\r\n', 
            '5':        ' 5\r\n', 
            '6':        ' 6\r\n', 
            '7':        ' 7\r\n', 
            '8':        ' 8\r\n', 
            '9':        ' 9\r\n', 
            '10':       ' 10\r\n', 
            '11':       ' 11\r\n', 
            '12':       ' 12\r\n', 
            '13':       ' 13\r\n', 
            '14':       ' 14\r\n', 
            '15':       ' 15\r\n', 
            '16':       ' 16\r\n', 
            '17':       ' 17\r\n', 
            '18':       ' 18\r\n', 
            '19':       ' 19\r\n', 
            '20':       ' 20\r\n', 
            '21':       ' 21\r\n', 
            '22':       ' 22\r\n', 
            '23':       ' 23\r\n', 
            '24':       ' 24\r\n'
        }

        ValueStateValues = {
            'Left':     'camera pan left', 
            'Right':    'camera pan right', 
            'Stop':     'camera pan stop\r\n'
        }

        if value in ValueStateValues and qualifier['Speed'] in PanSpeedStates:
            if value == 'Stop':
                PanCmdString = ValueStateValues[value]
            else:
                PanCmdString = ValueStateValues[value] + PanSpeedStates[qualifier['Speed']]

            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'camera standby off\r\n', 
            'Off':  'camera standby on\r\n'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
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

    def SetPresetTriSyncSave(self, value, qualifier):

        if 1 <= int(value) <= 16 and 1 <= int(qualifier['Speed']) <= 24:
            PresetTriSyncSaveCmdString = 'camera preset store {0} tri-sync {1}\r\n'.format(value, qualifier['Speed'])
            self.__SetHelper('PresetTriSyncSave', PresetTriSyncSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetTriSyncSave')

    def SetTilt(self, value, qualifier):

        TiltSpeedStates = {
            'Default':  '\r\n', 
            '1':        ' 1\r\n', 
            '2':        ' 2\r\n', 
            '3':        ' 3\r\n', 
            '4':        ' 4\r\n', 
            '5':        ' 5\r\n', 
            '6':        ' 6\r\n', 
            '7':        ' 7\r\n', 
            '8':        ' 8\r\n', 
            '9':        ' 9\r\n', 
            '10':       ' 10\r\n', 
            '11':       ' 11\r\n', 
            '12':       ' 12\r\n', 
            '13':       ' 13\r\n', 
            '14':       ' 14\r\n', 
            '15':       ' 15\r\n', 
            '16':       ' 16\r\n', 
            '17':       ' 17\r\n', 
            '18':       ' 18\r\n', 
            '19':       ' 19\r\n', 
            '20':       ' 20\r\n'
        }

        ValueStateValues = {
            'Up':   'camera tilt up', 
            'Down': 'camera tilt down', 
            'Stop': 'camera tilt stop\r\n'
        }

        if value in ValueStateValues and qualifier['Speed'] in TiltSpeedStates:
            if value == 'Stop':
                TiltCmdString = ValueStateValues[value]
            else:
                TiltCmdString = ValueStateValues[value] + TiltSpeedStates[qualifier['Speed']]

            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetZoom(self, value, qualifier):

        ZoomSpeedStates = {
            'Default':  '\r\n', 
            '1':        ' 1\r\n', 
            '2':        ' 2\r\n', 
            '3':        ' 3\r\n', 
            '4':        ' 4\r\n', 
            '5':        ' 5\r\n', 
            '6':        ' 6\r\n', 
            '7':        ' 7\r\n'
        }

        ValueStateValues = {
            'In'   : 'camera zoom in', 
            'Out'  : 'camera zoom out', 
            'Stop' : 'camera zoom stop\r\n'
        }

        if value in ValueStateValues and qualifier['Speed'] in ZoomSpeedStates:
            if value == 'Stop':
                ZoomCmdString = ValueStateValues[value]
            else:
                ZoomCmdString = ValueStateValues[value] + ZoomSpeedStates[qualifier['Speed']]

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

        self.Error(['An error occurred.'])

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