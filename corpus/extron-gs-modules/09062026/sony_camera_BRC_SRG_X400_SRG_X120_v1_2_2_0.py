from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import base64
from struct import pack, unpack
import re
import urllib.error
import urllib.request

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AddressSet': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'ExposureCompensationMode': {'Status': {}},
            'ExposureCompensationStep': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': {'Status': {}},
            'HighResolution': {'Status': {}},
            'HighSensitivity': {'Status': {}},
            'ImageFlip': {'Status': {}},
            'Iris': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PictureEffect': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

    def SetAddressSet(self, value, qualifier):

        AddressSetCmdString = b'\x88\x30\x01\xFF'
        self.__SetHelper('AddressSet', AddressSetCmdString, value, qualifier)

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority': 0x0B
        }

        if value in ValueStateValues:
            AutoExposureCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority'
        }
        AutoExposureCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        AutoFocusCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            BacklightCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        BacklightCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetExposureCompensationMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            ExposureCompensationModeCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x3E, ValueStateValues[value], 0xFF)
            self.__SetHelper('ExposureCompensationMode', ExposureCompensationModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExposureCompensationMode')

    def UpdateExposureCompensationMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        ExposureCompensationModeCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x3E, 0xFF)
        res = self.__UpdateHelper('ExposureCompensationMode', ExposureCompensationModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('ExposureCompensationMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Exposure Compensation Mode: Invalid/unexpected response'])

    def SetExposureCompensationStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            ExposureCompensationStepCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0E, ValueStateValues[value], 0xFF)
            self.__SetHelper('ExposureCompensationStep', ExposureCompensationStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExposureCompensationStep')

    def SetFocus(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Far': 0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            FocusCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            GainCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetHighResolution(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            HighResolutionCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x52, ValueStateValues[value], 0xFF)
            self.__SetHelper('HighResolution', HighResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHighResolution')

    def UpdateHighResolution(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        HighResolutionCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x52, 0xFF)
        res = self.__UpdateHelper('HighResolution', HighResolutionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('HighResolution', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['High Resolution: Invalid/unexpected response'])

    def SetHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            HighSensitivityCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x5E, ValueStateValues[value], 0xFF)
            self.__SetHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHighSensitivity')

    def UpdateHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        HighSensitivityCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x5E, 0xFF)
        res = self.__UpdateHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('HighSensitivity', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['High Sensitivity: Invalid/unexpected response'])

    def SetImageFlip(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            ImageFlipCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x66, ValueStateValues[value], 0xFF)
            self.__SetHelper('ImageFlip', ImageFlipCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageFlip')

    def UpdateImageFlip(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        ImageFlipCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x66, 0xFF)
        res = self.__UpdateHelper('ImageFlip', ImageFlipCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('ImageFlip', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Image Flip: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            IrisCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': pack('>6B', 0x81, 0x01, 0x06, 0x06, 0x10, 0xFF),
            'Enter': pack('>8B', 0x81, 0x01, 0x7E, 0x01, 0x02, 0x00, 0x01, 0xFF)
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up': 0x0301,
            'Down': 0x0302,
            'Left': 0x0103,
            'Right': 0x0203,
            'Up Left': 0x0101,
            'Up Right': 0x0201,
            'Down Left': 0x0102,
            'Down Right': 0x0202,
            'Stop': 0x0303,
            'Home': 0x04,
            'Reset': 0x05
        }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 23 and value in ValueStateValues:
            if value in {'Home', 'Reset'}:
                PanTiltCmdString = pack('>5B', 0x81, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', 0x81, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Black & White': 0x04,
            'Off': 0x00
        }

        if value in ValueStateValues:
            PictureEffectCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
            self.__SetHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureEffect')

    def UpdatePictureEffect(self, value, qualifier):

        ValueStateValues = {
            0x04: 'Black & White',
            0x00: 'Off'
        }
        PictureEffectCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x63, 0xFF)
        res = self.__UpdateHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('PictureEffect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Effect: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        PowerCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        preset = int(value)

        if 1 <= preset <= 100:
            preset -= 1
            PresetRecallCmdString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x02, preset, 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        preset = int(value)

        if 1 <= preset <= 100:
            preset -= 1
            PresetResetCmdString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x00, preset, 0xFF)
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        preset = int(value)

        if 1 <= preset <= 100:
            preset -= 1
            PresetSaveCmdString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, preset, 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            ShutterCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto 1': 0x00,
            'Auto 2': 0x04,
            'Indoor': 0x01,
            'Outdoor': 0x02,
            'Manual': 0x05,
            'One Push': 0x03
        }

        if value in ValueStateValues:
            WhiteBalanceCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF)
            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Auto 1',
            0x04: 'Auto 2',
            0x01: 'Indoor',
            0x02: 'Outdoor',
            0x05: 'Manual',
            0x03: 'One Push'
        }
        WhiteBalanceCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x35, 0xFF)
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            ZoomCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) == 4:
            error_map = {
                0x01: 'Message Length Error',
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable',
            }

            address, error_byte, error_code, terminator = unpack('>4B', response)
            if error_byte & 0x60 == 0x60:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map.get(error_code, 'Unknown Error'))])
                response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
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


class DeviceHTTPClass:
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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'HighResolution': { 'Status': {}},
            'HighSensitivity': { 'Status': {}},
            'ImageFlip': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters': ['Pan Tilt Speed'], 'Status': {}},
            'PictureEffect': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetReset': { 'Status': {}},
            'PresetSave': {'Parameters': ['Name','Thumbnail'], 'Status': {}},
            'Shutter': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }
            
    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'        : 'auto', 
            'Manual'           : 'manual', 
            'Shutter Priority' : 'shutter', 
            'Iris Priority'    : 'iris'
        }

        AutoExposureCmdString = 'command/imaging.cgi?ExposureMode={0}'.format(ValueStateValues[value])
        self.__SetHelper('AutoExposure', value, qualifier, AutoExposureCmdString)

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureValues = {
            'auto'    : 'Full Auto', 
            'manual'  : 'Manual', 
            'shutter' : 'Shutter Priority', 
            'iris'    : 'Iris Priority'
        }
        WhiteBalanceValues = {
            'auto'      : 'Auto 1', 
            'atw'       : 'Auto 2', 
            'indoor'    : 'Indoor', 
            'outdoor'   : 'Outdoor', 
            'manual'    : 'Manual', 
            'onepushwb' : 'One Push'
        }
        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        AutoExposureCmdString = 'command/inquiry.cgi?inq=imaging'
        res = self.__UpdateHelper('AutoExposure', value, qualifier, AutoExposureCmdString)
        if res:
            try:
                value = re.search('ExposureMode="?(auto|shutter|manual|iris)"?', res)
                self.WriteStatus('AutoExposure', AutoExposureValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

            try:
                value = re.search('BacklightCompensationMode="?(on|off)"?', res)
                self.WriteStatus('Backlight', ValueStateValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

            try:
                value = re.search('ExposureGain="?(1[0-7]|[1-9])"?', res)
                self.WriteStatus('Gain', int(value.group(1)), qualifier)
            except (ValueError, IndexError):
                self.Error(['Gain: Invalid/unexpected response'])

            try:
                value = re.search('HighResolutionMode="?(on|off)"?', res)
                self.WriteStatus('HighResolution', ValueStateValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['High Resolution: Invalid/unexpected response'])

            try:
                value = re.search('HighSensitivityMode="?(on|off)"?', res)
                self.WriteStatus('HighSensitivity', ValueStateValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['High Sensitivity: Invalid/unexpected response'])

            try:
                value = re.search('ExposureIris="?(2[0-5]|1?[0-9])"?', res)
                self.WriteStatus('Iris', int(value.group(1)), qualifier)
            except (ValueError, IndexError):
                self.Error(['Iris: Invalid/unexpected response'])

            try:
                value = re.search('ExposureExposureTime="?([6-9]|1[0-8])"?', res)
                self.WriteStatus('Shutter', int(value.group(1)), qualifier)
            except (ValueError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

            try:
                value = re.search('WhiteBalanceMode="?(auto|atw|indoor|outdoor|manual|onepushwb)"?', res)
                self.WriteStatus('WhiteBalance', WhiteBalanceValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'auto', 
            'Off' : 'manual'
        }

        AutoFocusCmdString = 'command/camera.cgi?FocusMode={0}'.format(ValueStateValues[value])
        self.__SetHelper('AutoFocus', value, qualifier, AutoFocusCmdString)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusValues = {
            'auto'   : 'On', 
            'manual' : 'Off'
        }
        ImageFlipValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }
        PictureEffectValues = {
            'bw'  : 'Black & White', 
            'off' : 'Off'
        }

        AutoFocusCmdString = 'command/inquiry.cgi?inq=camera'
        res = self.__UpdateHelper('AutoFocus', value, qualifier, AutoFocusCmdString)
        if res:
            try:
                value = re.search('FocusMode="?(auto|manual)"?', res)
                self.WriteStatus('AutoFocus', AutoFocusValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

            try:
                value = re.search('Eflip="?(on|off)"?', res)
                self.WriteStatus('ImageFlip', ImageFlipValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['Image Flip: Invalid/unexpected response'])

            try:
                value = re.search('PictureEffect="?(bw|off)"?', res)
                self.WriteStatus('PictureEffect', PictureEffectValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Effect: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        BacklightCmdString = 'command/imaging.cgi?BacklightCompensationMode={0}'.format(ValueStateValues[value])
        self.__SetHelper('Backlight', value, qualifier, BacklightCmdString)

    def UpdateBacklight(self, value, qualifier):

        self.UpdateAutoExposure(None, qualifier)
        
    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ValueStateValues = {
            'Far'  : 'far', 
            'Near' : 'near', 
        }

        speed_val = qualifier['Speed']
        if SpeedConstraints['Min'] <= speed_val <= SpeedConstraints['Max']:
            if value == 'Stop':
                FocusCmdString = 'command/ptzf.cgi?Move=stop,focus'
            else:
                FocusCmdString = 'command/ptzf.cgi?Move={0},{1}'.format(ValueStateValues[value], speed_val)
            self.__SetHelper('Focus', value, qualifier, FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 17
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GainCmdString = 'command/imaging.cgi?ExposureGain={0}'.format(value)
            self.__SetHelper('Gain', value, qualifier, GainCmdString)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        self.UpdateAutoExposure(None, qualifier)
            
    def SetHighResolution(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        HighResolutionCmdString = 'command/imaging.cgi?HighResolutionMode={0}'.format(ValueStateValues[value])
        self.__SetHelper('HighResolution', value, qualifier, HighResolutionCmdString)

    def UpdateHighResolution(self, value, qualifier):

        self.UpdateAutoExposure(None, qualifier)

    def SetHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        HighSensitivityCmdString = 'command/imaging.cgi?HighSensitivityMode={0}'.format(ValueStateValues[value])
        self.__SetHelper('HighSensitivity', value, qualifier, HighSensitivityCmdString)

    def UpdateHighSensitivity(self, value, qualifier):

        self.UpdateAutoExposure(None, qualifier)

    def SetImageFlip(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        ImageFlipCmdString = 'command/camera.cgi?Eflip={0}'.format(ValueStateValues[value])
        self.__SetHelper('ImageFlip', value, qualifier, ImageFlipCmdString)

    def UpdateImageFlip(self, value, qualifier):

        self.UpdateAutoFocus(None, qualifier)

    def SetIris(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 25
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            IrisCmdString = 'command/imaging.cgi?ExposureIris={0}'.format(value)
            self.__SetHelper('Iris', value, qualifier, IrisCmdString)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        self.UpdateAutoExposure(None, qualifier)

    def SetPanTilt(self, value, qualifier):

        PanTiltSpeedConstraints = {
            'Min' : 1,
            'Max' : 24
        }

        ValueStateValues = {
            'Up'         : 'up', 
            'Down'       : 'down', 
            'Left'       : 'left', 
            'Right'      : 'right', 
            'Up Left'    : 'up-left', 
            'Up Right'   : 'up-right', 
            'Down Left'  : 'down-left', 
            'Down Right' : 'down-right', 
        }

        speed_val = qualifier['Pan Tilt Speed']
        if PanTiltSpeedConstraints['Min'] <= speed_val <= PanTiltSpeedConstraints['Max']:
            if value == 'Stop':
                PanTiltCmdString = 'command/ptzf.cgi?Move=stop,pantilt'
            else:
                PanTiltCmdString = 'command/ptzf.cgi?Move={0},{1}'.format(ValueStateValues[value], speed_val)
            self.__SetHelper('PanTilt', value, qualifier, PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Black & White' : 'bw', 
            'Off'           : 'off'
        }

        PictureEffectCmdString = 'command/camera.cgi?PictureEffect={0}'.format(ValueStateValues[value])
        self.__SetHelper('PictureEffect', value, qualifier, PictureEffectCmdString)

    def UpdatePictureEffect(self, value, qualifier):

        self.UpdateAutoFocus(None, qualifier)
            
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'standby'
        }

        PowerCmdString = 'command/main.cgi?System={0}'.format(ValueStateValues[value])
        self.__SetHelper('Power', value, qualifier, PowerCmdString)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'on'      : 'On', 
            'standby' : 'Off'
        }

        PowerCmdString = 'command/inquiry.cgi?inq=system'
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString)
        if res:
            try:
                value = re.search('Power="?(on|standby)"?', res)
                self.WriteStatus('Power', ValueStateValues[value.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PresetRecallCmdString = 'command/presetposition.cgi?PresetCall={0}'.format(value)
            self.__SetHelper('PresetRecall', value, qualifier, PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PresetResetCmdString = 'command/presetposition.cgi?PresetClear={0}'.format(value)
            self.__SetHelper('PresetReset', value, qualifier, PresetResetCmdString)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        name_string = qualifier['Name']
        thumb_val = qualifier['Thumbnail']
        if 1 <= int(value) <= 100 and name_string and thumb_val in ('On', 'Off'):
            PresetSaveCmdString = 'command/presetposition.cgi?PresetSet={0},{1},{2}'.format(value, name_string, thumb_val.lower())
            self.__SetHelper('PresetSave', value, qualifier, PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueConstraints = {
            'Min' : 6,
            'Max' : 18
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ShutterCmdString = 'command/imaging.cgi?ExposureExposureTime={0}'.format(value)
            self.__SetHelper('Shutter', value, qualifier, ShutterCmdString)
        else:
            self.Discard('Invalid Command for SetShutter')

    def UpdateShutter(self, value, qualifier):

        self.UpdateAutoExposure(None, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto 1'   : 'auto', 
            'Auto 2'   : 'atw', 
            'Indoor'   : 'indoor', 
            'Outdoor'  : 'outdoor', 
            'Manual'   : 'manual', 
            'One Push' : 'onepushwb'
        }

        WhiteBalanceCmdString = 'command/imaging.cgi?WhiteBalanceMode={0}'.format(ValueStateValues[value])
        self.__SetHelper('WhiteBalance', value, qualifier, WhiteBalanceCmdString)

    def UpdateWhiteBalance(self, value, qualifier):

        self.UpdateAutoExposure(None, qualifier)
            
    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ValueStateValues = {
            'Tele' : 'tele', 
            'Wide' : 'wide', 
        }

        speed_val = qualifier['Speed']
        if SpeedConstraints['Min'] <= speed_val <= SpeedConstraints['Max']:
            if value == 'Stop':
                ZoomCmdString = 'command/ptzf.cgi?Move=stop,zoom'
            else:
                ZoomCmdString = 'command/ptzf.cgi?Move={0},{1}'.format(ValueStateValues[value], speed_val)
            self.__SetHelper('Zoom', value, qualifier, ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = ''.join([self.RootURL,url])
        headers = {'Content-Type': 'text/plain'}
        my_request = urllib.request.Request(url, data=None, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=5) # open() returns a http.client.HTTPResponse object if successful            
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202, 204):
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

        url = ''.join([self.RootURL,url])
        headers = {'Content-Type': 'text/plain'}
        my_request = urllib.request.Request(url, data=data, headers=headers)
        
        try:
            res = self.Opener.open(my_request, timeout=5) # open() returns a http.client.HTTPResponse object if successful
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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
