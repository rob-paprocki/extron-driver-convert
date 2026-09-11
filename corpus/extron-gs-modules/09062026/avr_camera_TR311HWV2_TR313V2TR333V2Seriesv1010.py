from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack
import time

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
            'AutoTracking': {'Status': {}},
            'Backlight': {'Status': {}},
            'FocusMode': {'Status': {}},
            'Gain': {'Status': {}},
            'Home': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PanTiltReset': {'Status': {}},
            'PeopleSize': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'Switch': {'Status': {}},
            'TrackingMode': {'Status': {}},
            'TrackingPoint': {'Status': {}},
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
            print('DeviceID set to an invalid value. It should be a number between 1-7.')

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':        0x00,
            'Manual':           0x03,
            'Shutter Priority': 0x0A, 
            'Iris Priority':    0x0B,
            'Bright':           0x0D
        }
        
        if value in ValueStateValues:
            AutoExposureCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutoExposureCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            AutoTrackingCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x7D, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            BacklightCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':     0x02,
            'Manual':   0x03
        }
        
        if value in ValueStateValues:
            FocusModeCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Auto', 
            0x03: 'Manual'
        }

        FocusModeCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            GainCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetHome(self, value, qualifier):

        HomeCmdString = pack('>5B', self._DeviceID, 0x01, 0x06, 0x04, 0xFF)
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            IrisCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])
        
        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Stop':         0x0303
        }
        
        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 24 and value in ValueStateValues:
            PanTiltCmdString = pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltReset(self, value, qualifier):

        PanTiltResetCmdString = pack('>5B', self._DeviceID, 0x01, 0x06, 0x05, 0xFF)
        self.__SetHelper('PanTiltReset', PanTiltResetCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            PowerCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPeopleSize(self, value, qualifier):

        ValueStateValues = {
            'Full Body':    0xA0,
            'Upper Body':   0xA1
        }

        if value in ValueStateValues:
            PeopleSizeCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, ValueStateValues[value], 0xFF)
            self.__SetHelper('PeopleSize', PeopleSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPeopleSize')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 255 and value not in [0x5F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6]:
            PresetRecallCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, int(value), 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 0 <= int(value) <= 255 and value not in [0x5F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6]:
            PresetResetCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x00, int(value), 0xFF)
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 255 and value not in [0x5F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6]:
            PresetSaveCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')  

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            ShutterCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetSwitch(self, value, qualifier):

        SwitchCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, 0xA3, 0xFF)
        self.__SetHelper('Switch', SwitchCmdString, value, qualifier)

    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Presenter':    0xA4,
            'Zone':         0xA5,
            'Hybrid':       0xA6
        }

        if value in ValueStateValues:
            TrackingModeCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, ValueStateValues[value], 0xFF)
            self.__SetHelper('TrackingMode', TrackingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingMode')

    def SetTrackingPoint(self, value, qualifier):

        TrackingPointCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, 0xA2, 0xFF)
        self.__SetHelper('TrackingPoint', TrackingPointCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        zoom_speed = int(qualifier['Zoom Speed'])
        
        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }
       
        if 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = 0x00
            else:
                zoom_speed += ValueStateValues[value]

            ZoomCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x07, zoom_speed, 0xFF)
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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoTracking': {'Status': {}},
            'Backlight': {'Status': {}},
            'FocusMode': {'Status': {}},
            'Gain': {'Status': {}},
            'Home': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PanTiltReset': {'Status': {}},
            'PeopleSize': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'Switch': {'Status': {}},
            'TrackingMode': {'Status': {}},
            'TrackingPoint': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

        self.PrevSequence = 0
        self.StartSequence = 0
        self.LastResetTime = 0

    def ResetSequence(self, value, qualifier):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def IncSequenceNumber(self):
        if self.StartSequence == 0:
            ctime = time.monotonic()
            if ctime - self.LastResetTime > 15:
                self.LastResetTime = ctime
                self.ResetSequence( None, None)
            self.PrevSequence = 1
        else:
            self.PrevSequence = (self.PrevSequence + 1) & 0xFFFFFFFF

        return pack('>I', self.PrevSequence)

    def SetHeader(self, commandstring):
        return b'\x01\x00\x00' + pack('B', len(commandstring)) + self.IncSequenceNumber() + commandstring

    def GetHeader(self, commandstring):
        return b'\x01\x10\x00' + pack('B', len(commandstring)) + self.IncSequenceNumber() + commandstring

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':        0x00,
            'Manual':           0x03,
            'Shutter Priority': 0x0A, 
            'Iris Priority':    0x0B,
            'Bright':           0x0D
        }
        
        if value in ValueStateValues:
            AutoExposureCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutoExposureCmdString = self.GetHeader(pack('>5B', 0x81, 0x09, 0x04, 0x39, 0xFF))
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            AutoTrackingCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x7D, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            BacklightCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF))
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':     0x02,
            'Manual':   0x03
        }
        
        if value in ValueStateValues:
            FocusModeCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF))
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Auto', 
            0x03: 'Manual'
        }

        FocusModeCmdString = self.GetHeader(pack('>5B', 0x81, 0x09, 0x04, 0x38, 0xFF))
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            GainCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF))
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetHome(self, value, qualifier):

        HomeCmdString = self.SetHeader(pack('>5B', 0x81, 0x01, 0x06, 0x04, 0xFF))
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            IrisCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF))
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])
        
        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Stop':         0x0303
        }
        
        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 24 and value in ValueStateValues:
            PanTiltCmdString = self.SetHeader(pack('>6BHB', 0x81, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF))
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltReset(self, value, qualifier):

        PanTiltResetCmdString = self.SetHeader(pack('>5B', 0x81, 0x01, 0x06, 0x05, 0xFF))
        self.__SetHelper('PanTiltReset', PanTiltResetCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            PowerCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = self.GetHeader(pack('>5B', 0x81, 0x09, 0x04, 0x00, 0xFF))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPeopleSize(self, value, qualifier):

        ValueStateValues = {
            'Full Body':    0xA0,
            'Upper Body':   0xA1
        }

        if value in ValueStateValues:
            PeopleSizeCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, ValueStateValues[value], 0xFF))
            self.__SetHelper('PeopleSize', PeopleSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPeopleSize')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 255 and value not in [0x5F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6]:
            PresetRecallCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x02, int(value), 0xFF))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 0 <= int(value) <= 255 and value not in [0x5F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6]:
            PresetResetCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x00, int(value), 0xFF))
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 255 and value not in [0x5F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6]:
            PresetSaveCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            ShutterCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF))
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetSwitch(self, value, qualifier):

        SwitchCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, 0xA3, 0xFF))
        self.__SetHelper('Switch', SwitchCmdString, value, qualifier)

    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Presenter':    0xA4,
            'Zone':         0xA5,
            'Hybrid':       0xA6
        }

        if value in ValueStateValues:
            TrackingModeCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, ValueStateValues[value], 0xFF))
            self.__SetHelper('TrackingMode', TrackingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingMode')

    def SetTrackingPoint(self, value, qualifier):

        TrackingPointCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, 0xA2, 0xFF))
        self.__SetHelper('TrackingPoint', TrackingPointCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        zoom_speed = int(qualifier['Zoom Speed'])
        
        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }
       
        if 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = 0x00
            else:
                zoom_speed += ValueStateValues[value]

            ZoomCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x07, zoom_speed, 0xFF))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if len(response) > 8:
            response = response[8:]

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
                if 'Power' == command:
                    self.StartSequence = 0
                return ''
            else:
                self.StartSequence = 1
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.PrevSequence = 0
        self.StartSequence = 0
        self.LastResetTime = 0

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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=52381, Model=None):
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