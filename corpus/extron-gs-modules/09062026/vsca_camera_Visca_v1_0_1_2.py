from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
from struct import pack

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

        self.deviceUsername = 'Username'
        self.devicePassword = None

        self._DeviceID = b'\x81'

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'BacklightMode': { 'Status': {}},
            'Focus': {'Parameters':['Focus Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'IRReceiver': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'RecallPreset': { 'Status': {}},
            'SavePreset': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = pack('B', 0x80 + int(value))

    def SetAutoExposure(self, value, qualifier):

        AutoExposureStateValues = {
            'Automatic Exposure Mode' : b'\x00', 
            'Manual Control Mode'     : b'\x03', 
            'Shutter Priority Mode'   : b'\x0A', 
            'Iris Priority Mode'      : b'\x0B', 
            'Bright Mode'             : b'\x0D'
        }
        AutoExposureCmdString = b''.join([self._DeviceID,b'\x01\x04\x39',AutoExposureStateValues[value],b'\xFF'])
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureStateValues = {
            b'\x00' : 'Automatic Exposure Mode', 
            b'\x03' : 'Manual Control Mode', 
            b'\x0A' : 'Shutter Priority Mode', 
            b'\x0B' : 'Iris Priority Mode', 
            b'\x0D' : 'Bright Mode'
        }
        AutoExposureCmdString = b''.join([self._DeviceID,b'\x09\x04\x39\xFF'])
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = AutoExposureStateValues[res[-2:-1]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        AutoFocusState = {
            'Auto'   : b'\x02', 
            'Manual' : b'\x03'
        }
        AutoFocusCmdString = b''.join([self._DeviceID,b'\x01\x04\x38',AutoFocusState[value],b'\xFF'])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusState = {
            b'\x02' : 'Auto', 
            b'\x03' : 'Manual'
        }
        AutoFocusCmdString = b''.join([self._DeviceID,b'\x09\x04\x38\xFF'])
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = AutoFocusState[res[-2:-1]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        BacklightModeStateValues = {
            'On'  : b'\x02', 
            'Off' : b'\x03'
        }
        BacklightModeCmdString = b''.join([self._DeviceID,b'\x01\x04\x33',BacklightModeStateValues[value],b'\xFF'])
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        BacklightModeStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }
        BacklightModeCmdString = b''.join([self._DeviceID,b'\x09\x04\x33\xFF'])
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = BacklightModeStateValues[res[-2:-1]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        FocusStateValues = {
            'Far'  : 0x20, 
            'Near' : 0x30, 
            'Stop' : 0x00
        }
        FocusSpd = int(qualifier['Focus Speed'])
        if 0 <= FocusSpd <= 7:
            if value == 'Stop':
                FocusSpeed = 0x00
            else:
                FocusSpeed = FocusSpd + FocusStateValues[value]
            FocusCmdString = b''.join([self._DeviceID,b'\x01\x04\x08',pack('B',FocusSpeed),b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        GainStateValues = {
            'Up'    : b'\x02', 
            'Down'  : b'\x03', 
            'Reset' : b'\x00'
        }
        GainCmdString = b''.join([self._DeviceID,b'\x01\x04\x0C',GainStateValues[value],b'\xFF'])
        self.__SetHelper('Gain', GainCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        IrisStateValues = {
            'Reset' : b'\x00', 
            'Up'    : b'\x02', 
            'Down'  : b'\x03'
        }
        IrisCmdString = b''.join([self._DeviceID,b'\x01\x04\x0B',IrisStateValues[value],b'\xFF'])
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetIRReceiver(self, value, qualifier):

        IRReceiverStateValues = {
            'On'  : b'\x02', 
            'Off' : b'\x03'
        }
        IRReceiverCmdString = b''.join([self._DeviceID,b'\x01\x06\x08',IRReceiverStateValues[value],b'\xFF'])
        self.__SetHelper('IRReceiver', IRReceiverCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        PanTiltStateValues = {
            'Up'         : b'\x03\x01', 
            'Down'       : b'\x03\x02', 
            'Left'       : b'\x01\x03', 
            'Right'      : b'\x02\x03', 
            'Up Left'    : b'\x01\x01', 
            'Up Right'   : b'\x02\x01', 
            'Down Left'  : b'\x01\x02', 
            'Down Right' : b'\x02\x02', 
            'Stop'       : b'\x03\x03'
        }
        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= PanSpd <= 24 and 1 <= TiltSpd <= 24:
            PanTiltCmdString = b''.join([self._DeviceID,b'\x01\x06\x01',pack('BB',PanSpd,TiltSpd),PanTiltStateValues[value],b'\xFF'])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : b'\x02', 
            'Off' : b'\x03'
        }
        PowerCmdString = b''.join([self._DeviceID,b'\x01\x04\x00',PowerStateValues[value],b'\xFF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }
        PowerCmdString = b''.join([self._DeviceID,b'\x09\x04\x00\xFF'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateValues[res[-2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        RecallPresetStateValues = {
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
        RecallPresetCmdString = b''.join([self._DeviceID,b'\x01\x04\x3F\x02',RecallPresetStateValues[value],b'\xFF'])
        self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)

    def SetSavePreset(self, value, qualifier):

        SavePresetStateValues = {
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
        SavePresetCmdString = b''.join([self._DeviceID,b'\x01\x04\x3F\x01',SavePresetStateValues[value],b'\xFF'])
        self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)

    def SetShutter(self, value, qualifier):

        ShutterStateValues = {
            'On'    : b'\x02', 
            'Off'   : b'\x03',
            'Reset' : b'\x00'
        }
        ShutterCmdString = b''.join([self._DeviceID,b'\x01\x04\x0A',ShutterStateValues[value],b'\xFF'])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'Tele' : 0x20, 
            'Wide' : 0x30, 
            'Stop' : 0x00
        }
        ZoomSpd = int(qualifier['Zoom Speed'])
        if 0 <= ZoomSpd <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = ZoomSpd + ZoomStateValues[value]
            ZoomCmdString = b''.join([self._DeviceID,b'\x01\x04\x07',pack('B',zoomSpeed),b'\xFF'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) > 3:
            ErrorCodes = {
                b'\x60\x02': 'Syntax Error',
                b'\x61\x02': 'Syntax Error',
                b'\x60\x03': 'Command Buffer Full',
                b'\x61\x03': 'Command Buffer Full',
                b'\x60\x04': 'Command Cancelled',
                b'\x61\x04': 'Command Cancelled',
                b'\x60\x05': 'No Socket',
                b'\x61\x05': 'No Socket',
                b'\x60\x41': 'Command Not Executable',
                b'\x61\x41': 'Command Not Executable'
            }
            if response[-3:-1] in ErrorCodes:
                self.Error([ErrorCodes[response[-3:-1]]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                res = ''
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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False

        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.SequenceNum = 1
        self._DeviceID = 0x81

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'BacklightMode': { 'Status': {}},
            'Focus': {'Parameters':['Focus Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'IRReceiver': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'RecallPreset': { 'Status': {}},
            'SavePreset': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
            }

    def SetAutoExposure(self, value, qualifier):

        AutoExposureStateValues = {
                'Automatic Exposure Mode' : 0x00, 
                'Manual Control Mode'     : 0x03, 
                'Shutter Priority Mode'   : 0x0A, 
                'Iris Priority Mode'      : 0x0B, 
                'Bright Mode'             : 0x0D
            }
        AutoExposureCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x39,AutoExposureStateValues[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureStateValues = {
            b'\x50\x00' : 'Automatic Exposure Mode',
            b'\x50\x03' : 'Manual Control Mode',
            b'\x50\x0A' : 'Shutter Priority Mode',
            b'\x50\x0B' : 'Iris Priority Mode',
            b'\x50\x0D' : 'Bright Mode'
        }
        AutoExposureCmdString = pack('>4BL5B',0x01,0x10,0x00,0x05,self.SequenceNum,self._DeviceID,0x09,0x04,0x39,0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = AutoExposureStateValues[res[-3:-1]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        AutoFocusState = {
                'Auto'   : 0x02, 
                'Manual' : 0x03
            }
        AutoFocusCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x38,AutoFocusState[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusState = {
            b'\x50\x02' : 'Auto',
            b'\x50\x03' : 'Manual'
        }
        AutoFocusCmdString = pack('>4BL5B',0x01,0x10,0x00,0x05,self.SequenceNum,self._DeviceID,0x09,0x04,0x38,0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = AutoFocusState[res[-3:-1]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        BacklightModeStateValues = {
                'On'  : 0x02, 
                'Off' : 0x03
            }
        BacklightModeCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x33,BacklightModeStateValues[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        BacklightModeStateValues = {
            b'\x50\x02' : 'On',
            b'\x50\x03' : 'Off'
        }
        BacklightModeCmdString = pack('>4BL5B',0x01,0x10,0x00,0x05,self.SequenceNum,self._DeviceID,0x09,0x04,0x33,0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = BacklightModeStateValues[res[-3:-1]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        FocusStateValues = {
            'Far'  : 0x20,
            'Near' : 0x30,
            'Stop' : 0x00
        }
        FocusSpd = int(qualifier['Focus Speed'])
        if 0 <= FocusSpd <= 7:
            if value == 'Stop':
                FocusSpeed = 0x00
            else:
                FocusSpeed = FocusSpd + FocusStateValues[value]
            FocusCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x08,FocusSpeed,0xFF)
            self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        GainStateValues = {
                'Up'    : 0x02, 
                'Down'  : 0x03, 
                'Reset' : 0x00
            }
        GainCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,1,4,0x0C,GainStateValues[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('Gain', GainCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        IrisStateValues = {
                'Reset' : 0x00, 
                'Up'    : 0x02, 
                'Down'  : 0x03
            }
        IrisCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x0B,IrisStateValues[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetIRReceiver(self, value, qualifier):

        IRReceiverStateValues = {
                'On'  : 0x02, 
                'Off' : 0x03
            }
        IRReceiverCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x06,0x08,IRReceiverStateValues[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('IRReceiver', IRReceiverCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        PanTiltStateValues = {
            'Up'         : 0x0301,
            'Down'       : 0x0302,
            'Left'       : 0x0103,
            'Right'      : 0x0203,
            'Up Left'    : 0x0101,
            'Up Right'   : 0x0201,
            'Down Left'  : 0x0102,
            'Down Right' : 0x0202,
            'Stop'       : 0x0303
        }
        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= PanSpd <= 24 and 1 <= TiltSpd <= 24:
            PanTiltCmdString = pack('>4BL6BHB',0x01,0x00,0x00,0x09,self.SequenceNum,self._DeviceID,0x01,0x06,0x01,PanSpd,TiltSpd,PanTiltStateValues[value],0xFF)
            self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
                'On'  : 0x02, 
                'Off' : 0x03
            }
        PowerCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x00,PowerStateValues[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            b'\x50\x02' : 'On',
            b'\x50\x03' : 'Off'
        }
        PowerCmdString = pack('>4BL5B',0x01,0x10,0x00,0x05,self.SequenceNum,self._DeviceID,0x09,0x04,0x00,0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateValues[res[-3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 16:
            RecallPresetCmdString = pack('>4BL7B',0x01,0x00,0x00,0x07,self.SequenceNum,self._DeviceID,0x01,0x04,0x3F,0x02,value-1,0xFF)
            self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetSavePreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            SavePresetCmdString = pack('>4BL7B',0x01,0x00,0x00,0x07,self.SequenceNum,self._DeviceID,0x01,0x04,0x3F,0x01,int(value)-1,0xFF)
            self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')

    def SetShutter(self, value, qualifier):

        ShutterStateValues = {
                'On'    : 2, 
                'Off'   : 3,
                'Reset' : 0
            }
        ShutterCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x0A,ShutterStateValues[value],0xFF)
        self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }
        ZoomSpd = int(qualifier['Zoom Speed'])
        if 0 <= ZoomSpd <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = ZoomSpd + ZoomStateValues[value]
            ZoomCmdString = pack('>4BL6B',0x01,0x00,0x00,0x06,self.SequenceNum,self._DeviceID,0x01,0x04,0x07,zoomSpeed,0xFF)
            self.SequenceNum = self.SequenceNum + 1 & 0xFFFFFFFF
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) > 3:
            ErrorCodes = {
                b'\x60\x02': 'Syntax Error',
                b'\x61\x02': 'Syntax Error',
                b'\x60\x03': 'Command Buffer Full',
                b'\x61\x03': 'Command Buffer Full',
                b'\x60\x04': 'Command Cancelled',
                b'\x61\x04': 'Command Cancelled',
                b'\x60\x05': 'No Socket',
                b'\x61\x05': 'No Socket',
                b'\x60\x41': 'Command Not Executable',
                b'\x61\x41': 'Command Not Executable'
            }
            if response[-3:-1] in ErrorCodes:
                self.Error([ErrorCodes[response[-3:-1]]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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
        self.SequenceNum = 1
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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