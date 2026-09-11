from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack


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

        self.Models = {
            'CV620': self.mrsh_19_2632_620,
            'CV620-IP': self.mrsh_19_2632_620IP,
            'CV620-NDI': self.mrsh_19_2632_620IP,
            'CV620-NDIW': self.mrsh_19_2632_620IP,
            'CV620-IPW': self.mrsh_19_2632_620IP,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture': {'Parameters':['Device ID'], 'Status': {}},
            'AutoExposure': {'Parameters':['Device ID'], 'Status': {}},
            'AutoFocusMode': {'Parameters':['Device ID'], 'Status': {}},
            'DigitalZoom': {'Parameters':['Device ID'], 'Status': {}},
            'Focus': {'Parameters':['Device ID','Speed'], 'Status': {}},
            'FocusMode': {'Parameters':['Device ID'], 'Status': {}},
            'Freeze': {'Parameters':['Device ID'], 'Status': {}},
            'Gain': {'Parameters':['Device ID','Position 1','Position 2'], 'Status': {}},
            'Iris': {'Parameters':['Device ID'], 'Status': {}},
            'IRReceive': {'Parameters':['Device ID'], 'Status': {}},
            'Mute': {'Parameters':['Device ID'], 'Status': {}},
            'PanTilt': {'Parameters':['Device ID','Pan Speed','Tilt Speed'], 'Status': {}},
            'PanTiltHome': {'Parameters':['Device ID'], 'Status': {}},
            'PanTiltReset': {'Parameters':['Device ID'], 'Status': {}},
            'PictureEffect': {'Parameters':['Device ID'], 'Status': {}},
            'Power': {'Parameters':['Device ID'], 'Status': {}},
            'PowerandConnection': { 'Status': {}},
            'PresetRecall': {'Parameters':['Device ID'], 'Status': {}},
            'PresetReset': {'Parameters':['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters':['Device ID'], 'Status': {}},
            'Resolution': {'Parameters':['Device ID'], 'Status': {}},
            'Shutter': {'Parameters':['Device ID'], 'Status': {}},
            'WhiteBalance': {'Parameters':['Device ID'], 'Status': {}},
            'Zoom': {'Parameters':['Device ID','Speed'], 'Status': {}},
            }

    def SetQualifierDeviceID(self, value):
        if 1 <= int(value) <= 7:
            return 0x80 + int(value)
        else:
            return None

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            ApertureCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
            self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAperture')

    def SetAutoExposure(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            AutoExposureCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x39, self.AutoExposureStateValues[value], 0xFF)
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            AutoExposureCmdString = pack('>5B', DeviceID, 0x09, 0x04, 0x39, 0xFF)
            res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
            if res:
                try:
                    value = self.AutoExposureStateNames[res[2]]
                    self.WriteStatus('AutoExposure', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Auto Exposure: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateAutoExposure')

    def SetAutoFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'        : 0x00, 
            'Interval'      : 0x01, 
            'Zoom Trigger'  : 0x02
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            AutoFocusModeCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x57, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocusMode', AutoFocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocusMode')

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On'    : 0x02, 
            'Off'   : 0x03
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            DigitalZoomCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x06, ValueStateValues[value], 0xFF)
            self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalZoom')

    def UpdateDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            DigitalZoomCmdString = pack('>5B', DeviceID, 0x09, 0x04, 0x06, 0xFF)
            res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('DigitalZoom', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Digital Zoom: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateDigitalZoom')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far' : 0x20,
            'Near': 0x30, 
            'Stop': 0x00
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID and 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                focusSpeed = 0x00
            else:
                focusSpeed = int(qualifier['Speed']) + ValueStateValues[value]
            FocusCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x08, focusSpeed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'          : 0x02, 
            'Manual'        : 0x03, 
            'Auto/Manual'   : 0x10             
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            if value == 'One Push Trigger':
                FocusModeCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x18, 0x01, 0xFF)
            else:
                FocusModeCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'Auto', 
            0x03 : 'Manual'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            FocusModeCmdString = pack('>5B', DeviceID, 0x09, 0x04, 0x38, 0xFF)
            res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('FocusMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Focus Mode: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateFocusMode')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x02,
            'Off': 0x03
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            FreezeCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x62, ValueStateValues[value], 0xFF)
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            FreezeCmdString = pack('>5B', DeviceID, 0x09, 0x04, 0x62, 0xFF)
            res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('Freeze', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Freeze: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def SetGain(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        Position1 = int(qualifier['Position 1'])
        Position2 = int(qualifier['Position 2'])
        if DeviceID and 0 <= Position1 <= 15 and 0 <= Position2 <= 15:
            GainCmdString = pack('>9B', DeviceID, 0x01, 0x04, 0x4C, 0x00, 0x00, Position1, Position2, 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            IrisCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetIRReceive(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            IRReceiveCmdString = pack('>6B', DeviceID, 0x01, 0x06, 0x08, ValueStateValues[value], 0xFF)
            self.__SetHelper('IRReceive', IRReceiveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRReceive')

    def UpdateIRReceive(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            IRReceiveCmdString = pack('>5B', DeviceID, 0x09, 0x06, 0x08, 0xFF)
            res = self.__UpdateHelper('IRReceive', IRReceiveCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('IRReceive', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['IR Receive: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateIRReceive')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            MuteCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x75, ValueStateValues[value], 0xFF)
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            MuteCmdString = pack('>5B', DeviceID, 0x09, 0x04, 0x75, 0xFF)
            res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('Mute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Mute: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateMute')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : [0x03,0x01],
            'Down'       : [0x03,0x02],
            'Left'       : [0x01,0x03],
            'Right'      : [0x02,0x03],
            'Up Left'    : [0x01,0x01],
            'Up Right'   : [0x02,0x01],
            'Down Left'  : [0x01,0x02],
            'Down Right' : [0x02,0x02],
            'Stop'       : [0x03,0x03],
            }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if DeviceID and 1 <= PanSpd <= 24 and 1 <= TiltSpd <= 24:
            PanTiltString = pack('>9B', DeviceID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltHome(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            PanTiltHomeCmdString = pack('>5B', DeviceID, 0x01, 0x06, 0x04, 0xFF)
            self.__SetHelper('PanTiltHome', PanTiltHomeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltHome')

    def SetPanTiltReset(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            PanTiltResetCmdString = pack('>5B', DeviceID, 0x01, 0x06, 0x05, 0xFF)
            self.__SetHelper('PanTiltReset', PanTiltResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltReset')

    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Off'       : 0x00, 
            'Neg Art'   : 0x02, 
            'B&W'       : 0x04
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            PictureEffectCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
            self.__SetHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureEffect')

    def UpdatePictureEffect(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Off', 
            0x02 : 'Neg Art', 
            0x04 : 'B&W'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            PictureEffectCmdString = pack('>5B', DeviceID, 0x09, 0x04, 0x63, 0xFF)
            res = self.__UpdateHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('PictureEffect', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture Effect: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdatePictureEffect')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x02,
            'Off': 0x03
            }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            PowerString = pack('>6B', DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetPower') 

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On',
            0x03 : 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            PowerString = pack('>5B', DeviceID, 0x09, 0x04, 0x00, 0xFF)
            res = self.__UpdateHelper('Power', PowerString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Inappropriate Command for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID and 0 <= int(value) <= 127:
            PresetString = pack('>7B',DeviceID, 0x01 ,0x04, 0x3F, 0x02, int(value), 0xFF)
            self.__SetHelper('PresetRecall', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID and 0 <= int(value) <= 127:
            PresetString = pack('>7B', DeviceID, 0x01, 0x04, 0x3F, 0x00, int(value), 0xFF)
            self.__SetHelper('PresetReset', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID and 0 <= int(value) <= 127:
            PresetString = pack('>7B', DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF)
            self.__SetHelper('PresetSave', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResolution(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            ResolutionCmdString = pack('>7B', DeviceID, 0x01, 0x06, 0x35, 0x00, self.ResolutionStateValues[value], 0xFF)
            self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResolution')

    def UpdateResolution(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            ResolutionCmdString = pack('>5B', DeviceID, 0x09, 0x06, 0x23, 0xFF)
            res = self.__UpdateHelper('Resolution', ResolutionCmdString, value, qualifier)
            if res:
                try:
                    value = self.ResolutionStateNames[res[2]]
                    self.WriteStatus('Resolution', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Resolution: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateResolution')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            ShutterCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetWhiteBalance(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            if value == 'One Push Trigger':
                WhiteBalanceCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x10, 0x05, 0xFF)
            else:
                WhiteBalanceCmdString = pack('>6B', DeviceID, 0x01, 0x04, 0x35, self.WhiteBalanceStateValues[value], 0xFF)
            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID:
            WhiteBalanceCmdString = pack('>5B', DeviceID, 0x09, 0x04, 0x35, 0xFF)
            res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
            if res:
                try:
                    value = self.WhiteBalanceStateNames[res[2]]
                    self.WriteStatus('WhiteBalance', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['White Balance: Invalid/unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateWhiteBalance')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In'    : 0x20,
            'Out'   : 0x30,
            'Stop'  : 0x00
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID and 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomString = pack('>6B', DeviceID, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response.count == 4:
                address, errorByte, errorCode, terminator = unpack('>BBBB', response)
                if (errorByte == 0x60) and ( errorCode == 0x02 ):
                    self.Error([sourceCmdName + ' Syntax Error'])
                    response = ''
                elif (errorByte == 0x60) and ( errorCode == 0x03 ):
                    self.Error([sourceCmdName + ' Command Buffer Full'])
                    response = ''
                elif (errorByte in [0x60,0x61,0x62]) and ( errorCode == 0x04 ):
                    self.Error([sourceCmdName + ' Command Cancelled'])
                    response = ''
                elif (errorByte in [0x60,0x61,0x62]) and ( errorCode == 0x05 ):
                    self.Error([sourceCmdName + ' No Socket (To Be Cancelled)'])
                    response = ''
                elif (errorByte in [0x60,0x61,0x62]) and ( errorCode == 0x41 ):
                    self.Error([sourceCmdName + ' Command Not Executable'])
                    response = ''
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
                res = self.__CheckResponseForErrors(command + ':', res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen = 4)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def mrsh_19_2632_620(self):
        self.AutoExposureStateValues = {
            'Full Auto'        : 0x00, 
            'Manual'           : 0x03, 
            'Shutter Priority' : 0x0A, 
            'Iris Priority'    : 0x0B, 
            'Bright'           : 0x0D
        }
        self.AutoExposureStateNames = {
            0x00 : 'Full Auto', 
            0x03 : 'Manual', 
            0x0A : 'Shutter Priority', 
            0x0B : 'Iris Priority', 
            0x0D : 'Bright'
        }
        self.ResolutionStateValues = {
            '1080p-60Hz'    : 0x00, 
            '1080p-50Hz'    : 0x01, 
            '1080p-30Hz'    : 0x02, 
            '1080p-25Hz'    : 0x03, 
            '1080i-60Hz'    : 0x04, 
            '1080i-50Hz'    : 0x05, 
            '720p-60Hz'     : 0x06, 
            '720p-50Hz'     : 0x07, 
            '720p-30Hz'     : 0x08, 
            '720p-25Hz'     : 0x09, 
            '1080p-59.94Hz' : 0x0A, 
            '1080i-59.94Hz' : 0x0B, 
            '1080p-29.97Hz' : 0x0C, 
            '720p-59.94Hz'  : 0x0D, 
            '720p-29.97Hz'  : 0x0E
        }
        self.ResolutionStateNames = {
            0x00 : '1080p-60Hz', 
            0x01 : '1080p-50Hz', 
            0x02 : '1080p-30Hz', 
            0x03 : '1080p-25Hz', 
            0x04 : '1080i-60Hz', 
            0x05 : '1080i-50Hz', 
            0x06 : '720p-60Hz', 
            0x07 : '720p-50Hz', 
            0x08 : '720p-30Hz', 
            0x09 : '720p-25Hz', 
            0x0A : '1080p-59.94Hz', 
            0x0B : '1080i-59.94Hz', 
            0x0C : '1080p-29.97Hz', 
            0x0D : '720p-59.94Hz', 
            0x0E : '720p-29.97Hz'
        }
        self.WhiteBalanceStateValues = {
            'Auto'                      : 0x00, 
            'Indoor'                    : 0x01, 
            'Outdoor'                   : 0x02, 
            'One Push'                  : 0x03, 
            'ATW'                       : 0x04,
            'Manual'                    : 0x05, 
            'Outdoor Auto'              : 0x06, 
            'Sodium Lamp Auto'          : 0x07, 
            'Sodium Lamp'               : 0x08, 
            'Sodium Lamp Outdoor Auto'  : 0x09, 
        }
        self.WhiteBalanceStateNames = {
            0x00 : 'Auto', 
            0x01 : 'Indoor', 
            0x02 : 'Outdoor', 
            0x03 : 'One Push', 
            0x04 : 'ATW', 
            0x05 : 'Manual', 
            0x06 : 'Outdoor Auto', 
            0x07 : 'Sodium Lamp Auto', 
            0x08 : 'Sodium Lamp', 
            0x09 : 'Sodium Lamp Outdoor Auto' 
        }


    def mrsh_19_2632_620IP(self):
        self.AutoExposureStateValues = {
            'Full Auto'        : 0x00, 
            'Manual'           : 0x03, 
            'Shutter Priority' : 0x0A, 
            'Iris Priority'    : 0x0B, 
            'White Board'      : 0x5F, 
            'Smooth Auto'      : 0x60
        }
        self.AutoExposureStateNames = {
            0x00 : 'Full Auto', 
            0x03 : 'Manual', 
            0x0A : 'Shutter Priority', 
            0x0B : 'Iris Priority', 
            0x5F : 'White Board', 
            0x60 : 'Smooth Auto'
        }
        self.ResolutionStateValues = {
            '1080p-60Hz'    : 0x00, 
            '1080p-59.94Hz' : 0x01, 
            '1080p-50Hz'    : 0x02, 
            '1080p-30Hz'    : 0x03, 
            '1080p-29.97Hz' : 0x04, 
            '1080p-25Hz'    : 0x05, 
            '1080i-60Hz'    : 0x06, 
            '1080i-59.94Hz' : 0x07, 
            '1080i-50Hz'    : 0x08, 
            '720p-60Hz'     : 0x09, 
            '720p-59.94Hz'  : 0x0A, 
            '720p-50Hz'     : 0x0B
        }
        self.ResolutionStateNames = {
            0x00 : '1080p-60Hz', 
            0x01 : '1080p-59.94Hz', 
            0x02 : '1080p-50Hz', 
            0x03 : '1080p-30Hz', 
            0x04 : '1080p-29.97Hz', 
            0x05 : '1080p-25Hz', 
            0x06 : '1080i-60Hz', 
            0x07 : '1080i-59.94Hz', 
            0x08 : '1080i-50Hz', 
            0x09 : '720p-60Hz', 
            0x0A : '720p-59.94Hz', 
            0x0B : '720p-50Hz'
        }
        self.WhiteBalanceStateValues = {
            'Auto'          : 0x00, 
            'Indoor'        : 0x01, 
            'Outdoor'       : 0x02, 
            'One Push'      : 0x03, 
            'ATW'           : 0x04,
            'Manual'        : 0x05,
            'Sodium Lamp'   : 0x06, 
            '3000K'         : 0x07, 
            '4300K'         : 0x08, 
            '5000K'         : 0x09, 
            '6500K'         : 0x0A, 
            '8000K'         : 0x0B, 
            'Wide Auto'     : 0x0C 
        }
        self.WhiteBalanceStateNames = {
            0x00 : 'Auto', 
            0x01 : 'Indoor', 
            0x02 : 'Outdoor', 
            0x03 : 'One Push', 
            0x04 : 'ATW', 
            0x05 : 'Manual',
            0x06 : 'Sodium Lamp', 
            0x07 : '3000K', 
            0x08 : '4300K', 
            0x09 : '5000K', 
            0x0A : '6500K', 
            0x0B : '8000K', 
            0x0C : 'Wide Auto'
        }
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture': { 'Status': {}},
            'AutoExposure': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Gain': {'Parameters':['Position 1','Position 2'], 'Status': {}},
            'Iris': { 'Status': {}},
            'IRReceive': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'PanTiltHome': { 'Status': {}},
            'PanTiltReset': { 'Status': {}},
            'PictureEffect': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetReset': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Resolution': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
            }

        self.PrevSequence = 0
        self.StartSequence = 0

    def ResetSequence(self):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def IncSequenceNumber(self):
        if self.StartSequence == 0:
           self.ResetSequence()
           self.PrevSequence = 1
           Sequence = b'\x00\x00\x00\x01'
        else:
            self.PrevSequence = self.PrevSequence + 1 if self.PrevSequence < 4294967295 else 0
            Sequence = pack('>L', self.PrevSequence)
        return Sequence
        
    def SetHeader(self, commandstring):
        sequence = self.IncSequenceNumber()
        commandstring = b'\x01\x00\x00' + pack('B', len(commandstring)) + sequence + b'\x81' + commandstring[1:]
        return commandstring            

    def GetHeader(self, commandstring):
        sequence = self.IncSequenceNumber()
        commandstring = b'\x01\x10\x00' + pack('B', len(commandstring)) + sequence + b'\x81' + commandstring[1:]
        return commandstring

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }
        ApertureCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', self.SetHeader(ApertureCmdString), value, qualifier)

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'        : 0x00, 
            'Manual'           : 0x03, 
            'Shutter Priority' : 0x0A, 
            'Iris Priority'    : 0x0B, 
            'White Board'      : 0x5F, 
            'Smooth Auto'      : 0x60
        }
        AutoExposureCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoExposure', self.SetHeader(AutoExposureCmdString), value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Full Auto', 
            0x03 : 'Manual', 
            0x0A : 'Shutter Priority', 
            0x0B : 'Iris Priority', 
            0x5F : 'White Board', 
            0x60 : 'Smooth Auto'
        }
        AutoExposureCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', self.GetHeader(AutoExposureCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected Response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far' : 0x20,
            'Near': 0x30, 
            'Stop': 0x00
        }
        if 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                focusSpeed = 0x00
            else:
                focusSpeed = int(qualifier['Speed']) + ValueStateValues[value]
            FocusCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x08, focusSpeed, 0xFF)
            self.__SetHelper('Focus', self.SetHeader(FocusCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'          : 0x02, 
            'Manual'        : 0x03, 
            'Auto/Manual'   : 0x10             
        }
        if value == 'One Push Trigger':
            FocusModeCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x18, 0x01, 0xFF)
        else:
            FocusModeCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('FocusMode', self.SetHeader(FocusModeCmdString), value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'Auto', 
            0x03 : 'Manual'
        }
        FocusModeCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('FocusMode', self.GetHeader(FocusModeCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected Response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x02,
            'Off': 0x03
        }
        FreezeCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x62, ValueStateValues[value], 0xFF)
        self.__SetHelper('Freeze', self.SetHeader(FreezeCmdString), value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }
        FreezeCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x62, 0xFF)
        res = self.__UpdateHelper('Freeze', self.GetHeader(FreezeCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected Response'])

    def SetGain(self, value, qualifier):

        Position1 = int(qualifier['Position 1'])
        Position2 = int(qualifier['Position 2'])
        if 0 <= Position1 <= 15 and 0 <= Position2 <= 15:
            GainCmdString = pack('>9B', 0x81, 0x01, 0x04, 0x4C, 0x00, 0x00, Position1, Position2, 0xFF)
            self.__SetHelper('Gain', self.SetHeader(GainCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }
        IrisCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', self.SetHeader(IrisCmdString), value, qualifier)

    def SetIRReceive(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }
        IRReceiveCmdString = pack('>6B', 0x81, 0x01, 0x06, 0x08, ValueStateValues[value], 0xFF)
        self.__SetHelper('IRReceive', self.SetHeader(IRReceiveCmdString), value, qualifier)

    def UpdateIRReceive(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }
        IRReceiveCmdString = pack('>5B', 0x81, 0x09, 0x06, 0x08, 0xFF)
        res = self.__UpdateHelper('IRReceive', self.GetHeader(IRReceiveCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('IRReceive', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Receive: Invalid/unexpected Response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }
        MuteCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x75, ValueStateValues[value], 0xFF)
        self.__SetHelper('Mute', self.SetHeader(MuteCmdString), value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }
        MuteCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x75, 0xFF)
        res = self.__UpdateHelper('Mute', self.GetHeader(MuteCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected Response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : [0x03,0x01],
            'Down'       : [0x03,0x02],
            'Left'       : [0x01,0x03],
            'Right'      : [0x02,0x03],
            'Up Left'    : [0x01,0x01],
            'Up Right'   : [0x02,0x01],
            'Down Left'  : [0x01,0x02],
            'Down Right' : [0x02,0x02],
            'Stop'       : [0x03,0x03],
            }
        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= PanSpd <= 24 and 1 <= TiltSpd <= 24:
            PanTiltString = pack('>9B', 0x81, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', self.SetHeader(PanTiltString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltHome(self, value, qualifier):

        PanTiltHomeCmdString = pack('>5B', 0x81, 0x01, 0x06, 0x04, 0xFF)
        self.__SetHelper('PanTiltHome', self.SetHeader(PanTiltHomeCmdString), value, qualifier)

    def SetPanTiltReset(self, value, qualifier):

        PanTiltResetCmdString = pack('>5B', 0x81, 0x01, 0x06, 0x05, 0xFF)
        self.__SetHelper('PanTiltReset', self.SetHeader(PanTiltResetCmdString), value, qualifier)

    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Off'       : 0x00, 
            'Neg Art'   : 0x02, 
            'B&W'       : 0x04
        }
        PictureEffectCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
        self.__SetHelper('PictureEffect', self.SetHeader(PictureEffectCmdString), value, qualifier)

    def UpdatePictureEffect(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Off', 
            0x02 : 'Neg Art', 
            0x04 : 'B&W'
        }
        PictureEffectCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x63, 0xFF)
        res = self.__UpdateHelper('PictureEffect', self.GetHeader(PictureEffectCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('PictureEffect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Effect: Invalid/unexpected Response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x02,
            'Off': 0x03
        }
        PowerString = pack('>6B', 0x81, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', self.SetHeader(PowerString), value, qualifier) 

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On',
            0x03 : 'Off'
        }
        
        PowerString = pack('>5B', 0x81, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', self.GetHeader(PowerString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetString = pack('>7B',0x81, 0x01 ,0x04, 0x3F, 0x02, int(value), 0xFF)
            self.__SetHelper('PresetRecall', self.SetHeader(PresetString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x00, int(value), 0xFF)
            self.__SetHelper('PresetReset', self.SetHeader(PresetString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF)
            self.__SetHelper('PresetSave', self.SetHeader(PresetString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResolution(self, value, qualifier):

        ValueStateValues = {
            '1080p-60Hz'    : 0x00, 
            '1080p-59.94Hz' : 0x01, 
            '1080p-50Hz'    : 0x02, 
            '1080p-30Hz'    : 0x03, 
            '1080p-29.97Hz' : 0x04, 
            '1080p-25Hz'    : 0x05, 
            '1080i-60Hz'    : 0x06, 
            '1080i-59.94Hz' : 0x07, 
            '1080i-50Hz'    : 0x08, 
            '720p-60Hz'     : 0x09, 
            '720p-59.94Hz'  : 0x0A, 
            '720p-50Hz'     : 0x0B
        }
        ResolutionCmdString = pack('>7B', 0x81, 0x01, 0x06, 0x35, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Resolution', self.SetHeader(ResolutionCmdString), value, qualifier)

    def UpdateResolution(self, value, qualifier):

        ValueStateValues = {
            0x00 : '1080p-60Hz', 
            0x01 : '1080p-59.94Hz', 
            0x02 : '1080p-50Hz', 
            0x03 : '1080p-30Hz', 
            0x04 : '1080p-29.97Hz', 
            0x05 : '1080p-25Hz', 
            0x06 : '1080i-60Hz', 
            0x07 : '1080i-59.94Hz', 
            0x08 : '1080i-50Hz', 
            0x09 : '720p-60Hz', 
            0x0A : '720p-59.94Hz', 
            0x0B : '720p-50Hz'
        }        
        ResolutionCmdString = pack('>5B', 0x81, 0x09, 0x06, 0x23, 0xFF)
        res = self.__UpdateHelper('Resolution', self.GetHeader(ResolutionCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Resolution', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Resolution: Invalid/unexpected Response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }
        ShutterCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
        self.__SetHelper('Shutter', self.SetHeader(ShutterCmdString), value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto'          : 0x00, 
            'Indoor'        : 0x01, 
            'Outdoor'       : 0x02, 
            'One Push'      : 0x03, 
            'ATW'           : 0x04,
            'Manual'        : 0x05,
            'Sodium Lamp'   : 0x06, 
            '3000K'         : 0x07, 
            '4300K'         : 0x08, 
            '5000K'         : 0x09, 
            '6500K'         : 0x0A, 
            '8000K'         : 0x0B, 
            'Wide Auto'     : 0x0C 
        }
        if value == 'One Push Trigger':
            WhiteBalanceCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x10, 0x05, 0xFF)
        else:
            WhiteBalanceCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF)
        self.__SetHelper('WhiteBalance', self.SetHeader(WhiteBalanceCmdString), value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Auto', 
            0x01 : 'Indoor', 
            0x02 : 'Outdoor', 
            0x03 : 'One Push', 
            0x04 : 'ATW', 
            0x05 : 'Manual',
            0x06 : 'Sodium Lamp', 
            0x07 : '3000K', 
            0x08 : '4300K', 
            0x09 : '5000K', 
            0x0A : '6500K', 
            0x0B : '8000K', 
            0x0C : 'Wide Auto'
        }
        WhiteBalanceCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x35, 0xFF)
        res = self.__UpdateHelper('WhiteBalance', self.GetHeader(WhiteBalanceCmdString), value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected Response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In'    : 0x20,
            'Out'   : 0x30,
            'Stop'  : 0x00
        }
        if 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomString = pack('>6B', 0x81, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', self.SetHeader(ZoomString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response.count == 4:
                address, errorByte, errorCode, terminator = unpack('>BBBB', response)

                if (errorByte == 0x60) and ( errorCode == 0x02 ):
                    self.Error([sourceCmdName + ' Syntax Error'])
                    response = ''
                elif (errorByte == 0x60) and ( errorCode == 0x03 ):
                    self.Error([sourceCmdName + ' Command Buffer Full'])
                    response = ''
                elif (errorByte in [0x60,0x61,0x62]) and ( errorCode == 0x04 ):
                    self.Error([sourceCmdName + ' Command Cancelled'])
                    response = ''
                elif (errorByte in [0x60,0x61,0x62]) and ( errorCode == 0x05 ):
                    self.Error([sourceCmdName + ' No Socket (To Be Cancelled)'])
                    response = ''
                elif (errorByte in [0x60,0x61,0x62]) and ( errorCode == 0x41 ):
                    self.Error([sourceCmdName + ' Command Not Executable'])
                    response = ''
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
                res = self.__CheckResponseForErrors(command + ':' , res[8:12])

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
                self.StartSequence = 0
                return ''
            else:
                self.StartSequence = 1
                return self.__CheckResponseForErrors(command + ':' , res[8:12])


    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.ResetSequence()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.StartSequence = 0
        self.PrevSequence = 0

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)


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