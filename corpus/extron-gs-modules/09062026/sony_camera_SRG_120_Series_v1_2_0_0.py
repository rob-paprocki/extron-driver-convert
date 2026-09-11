from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack


class DeviceClass:

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
            'Aperture': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoExposure': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoFocus': {'Parameters': ['Device ID'], 'Status': {}},
            'BacklightMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'DigitalZoom': {'Parameters': ['Device ID'], 'Status': {}},
            'ExposureCompAmount': {'Parameters': ['Device ID'], 'Status': {}},
            'Exposurecompensation': {'Parameters': ['Device ID'], 'Status': {}},
            'Focus': {'Parameters': ['Device ID', 'Speed'], 'Status': {}},
            'Gain': {'Parameters': ['Device ID'], 'Status': {}},
            'HighResolution': {'Parameters': ['Device ID'], 'Status': {}},
            'HighSensitivity': {'Parameters': ['Device ID'], 'Status': {}},
            'Iris': {'Parameters': ['Device ID'], 'Status': {}},
            'PanTilt': {'Parameters': ['Device ID', 'Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PictureEffect': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'Preset': {'Parameters': ['Device ID', 'Action'], 'Status': {}},
            'Shutter': {'Parameters': ['Device ID'], 'Status': {}},
            'WideDynamicRange': {'Parameters': ['Device ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Device ID', 'Speed'], 'Status': {}}
        }

    def SetDeviceID(self, value):
        try:
            value = int(value)
        except ValueError:
            return 0
        if 1 <= value <= 7:
            return 0x80 + value
        else:
            return 0

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            ApertureCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
            self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAperture')

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Shutter': 0x0A,
            'Iris': 0x0B,
            'Bright': 0x0D
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            AutoExposureCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Full Auto',
            b'\x03': 'Manual',
            b'\x0A': 'Shutter',
            b'\x0B': 'Iris',
            b'\x0D': 'Bright'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            AutoExposureCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x39, 0xFF)
            res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('AutoExposure', value, qualifier)
                except (KeyError, IndexError):
                    print('Auto Exposure: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateAutoExposure')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            AutoFocusCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            AutoFocusCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x38, 0xFF)
            res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('AutoFocus', value, qualifier)
                except (KeyError, IndexError):
                    print('Auto Focus: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateAutoFocus')

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            BacklightModeCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBacklightMode')

    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            BacklightModeCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x33, 0xFF)
            res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('BacklightMode', value, qualifier)
                except (KeyError, IndexError):
                    print('Backlight Mode: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateBacklightMode')

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            BrightnessCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0D, ValueStateValues[value], 0xFF)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBrightness')

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            DigitalZoomCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x06, ValueStateValues[value], 0xFF)
            self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDigitalZoom')

    def UpdateDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            DigitalZoomCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x06, 0xFF)
            res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('DigitalZoom', value, qualifier)
                except (KeyError, IndexError):
                    print('Digital Zoom: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateDigitalZoom')

    def SetExposureCompAmount(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            ExposureCompAmountCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0E, ValueStateValues[value], 0xFF)
            self.__SetHelper('ExposureCompAmount', ExposureCompAmountCmdString, value, qualifier)
        else:
            print('Invalid Command for SetExposureCompAmount')

    def SetExposurecompensation(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03,
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            ExposurecompensationCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x3E, ValueStateValues[value], 0xFF)
            self.__SetHelper('Exposurecompensation', ExposurecompensationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetExposurecompensation')

    def UpdateExposurecompensation(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off',
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            ExposurecompensationCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x3E, 0xFF)
            res = self.__UpdateHelper('Exposurecompensation', ExposurecompensationCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Exposurecompensation', value, qualifier)
                except (KeyError, IndexError):
                    print('Exposure Compensation: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateExposurecompensation')

    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min': 0,
            'Max': 7
        }
        ValueStateValues = {
            'Far': 0x20,
            'Near': 0x30
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        speed = int(qualifier['Speed'])
        if cameraID and SpeedConstraints['Min'] <= speed <= SpeedConstraints['Max']:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            FocusCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            GainCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetGain')

    def SetHighResolution(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            HighResolutionCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x52, ValueStateValues[value], 0xFF)
            self.__SetHelper('HighResolution', HighResolutionCmdString, value, qualifier)
        else:
            print('Invalid Command for SetHighResolution')

    def UpdateHighResolution(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            HighResolutionCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x52, 0xFF)
            res = self.__UpdateHelper('HighResolution', HighResolutionCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('HighResolution', value, qualifier)
                except (KeyError, IndexError):
                    print('High Resolution: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateHighResolution')

    def SetHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            HighSensitivityCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x5E, ValueStateValues[value], 0xFF)
            self.__SetHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)
        else:
            print('Invalid Command for SetHighSensitivity')

    def UpdateHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            HighSensitivityCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x5E, 0xFF)
            res = self.__UpdateHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('HighSensitivity', value, qualifier)
                except (KeyError, IndexError):
                    print('High Sensitivity: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateHighSensitivity')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            IrisCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            print('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min': 1,
            'Max': 24
        }
        TiltSpeedConstraints = {
            'Min': 1,
            'Max': 20
        }
        ValueStateValues = {
            'Up': 0x0301,
            'Down': 0x0302,
            'Left': 0x0103,
            'Right': 0x0203,
            'Stop': 0x0303,
            'Up Left': 0x0101,
            'Up Right': 0x0201,
            'Down Left': 0x0102,
            'Down Right': 0x0202,
            'Home': 0x04,
            'Reset': 0x05
        }

        cameraID = self.SetDeviceID(qualifier['Device ID'])
        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if cameraID and value not in ('Home', 'Reset'):
            if (PanSpeedConstraints['Min'] <= PanSpd <= PanSpeedConstraints['Max']) and (TiltSpeedConstraints['Min'] <= TiltSpd <= TiltSpeedConstraints['Max']):
                PanTiltCmdString = pack('>6BHB', cameraID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value], 0xFF)
                self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        elif cameraID and value in ('Home', 'Reset'):
            PanTiltCmdString = pack('>5B', cameraID, 0x01, 0x06, ValueStateValues[value], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanTilt')

    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Off': 0x00,
            'Negative': 0x02,
            'B&W': 0x04
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            PictureEffectCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
            self.__SetHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPictureEffect')

    def UpdatePictureEffect(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x02': 'Negative',
            b'\x04': 'B&W'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            PictureEffectCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x63, 0xFF)
            res = self.__UpdateHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('PictureEffect', value, qualifier)
                except (KeyError, IndexError):
                    print('Picture Effect: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdatePictureEffect')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            PowerCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            PowerCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x00, 0xFF)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    print('Power: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdatePower')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': 0x01,
            'Reset': 0x00,
            'Recall': 0x02
        }
        ValueConstraints = {
            'Min': 1,
            'Max': 16,
        }
        Action = qualifier['Action']
        value = int(value)
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID and ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Action in ActionStates:
            PresetCmdString = pack('>7B', cameraID, 0x01, 0x04, 0x3F, ActionStates[Action], value - 1, 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            ShutterCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            print('Invalid Command for SetShutter')

    def SetWideDynamicRange(self, value, qualifier):

        ValueStateValues = {
            'Low': 0x01,
            'Mid': 0x02,
            'High': 0x03,
            'Off': 0x00
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            WideDynamicRangeCmdString = pack('>7B', cameraID, 0x01, 0x7E, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('WideDynamicRange', WideDynamicRangeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetWideDynamicRange')

    def UpdateWideDynamicRange(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Low',
            b'\x02': 'Mid',
            b'\x03': 'High',
            b'\x00': 'Off'
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        if cameraID:
            WideDynamicRangeCmdString = pack('>6B', cameraID, 0x09, 0x7E, 0x04, 0x00, 0xFF)
            res = self.__UpdateHelper('WideDynamicRange', WideDynamicRangeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('WideDynamicRange', value, qualifier)
                except (KeyError, IndexError):
                    print('Wide Dynamic Range: Invalid/unexpected response')
        else:
            print('Invalid Command for UpdateWideDynamicRange')

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 0,
            'Max': 7
        }
        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30
        }
        cameraID = self.SetDeviceID(qualifier['Device ID'])
        speed = int(qualifier['Speed'])
        if cameraID and SpeedConstraints['Min'] <= speed <= SpeedConstraints['Max']:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            ZoomCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                Errors = {
                    0x01: ': Message Length Error',
                    0x02: ': Syntax Error',
                    0x03: ': Command Buffer Full',
                    0x04: ': Command Cancelled',
                    0x05: ': No Socket',
                    0x41: ': Command Not Executable',
                }
                address, errorbyte, errorcode, terminator = unpack('>4B', response)
                if errorbyte & 0x60 == 0x60:
                    print('sourceCmdName' + Errors.get(errorcode) + 'Unknown Error Occured')
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('No response received for ', command)
            else:
                res = self.__CheckResponseForErrors(command, res)

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
