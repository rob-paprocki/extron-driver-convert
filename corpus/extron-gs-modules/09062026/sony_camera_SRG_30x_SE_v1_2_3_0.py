from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface
from extronlib import event
import re, time
from struct import pack, unpack
from collections import deque
from extronlib.system import Wait

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
            'Aperture': {'Parameters': ['Camera ID'], 'Status': {}},
            'AutoExposure': {'Parameters': ['Camera ID'], 'Status': {}},
            'AutoFocus': {'Parameters': ['Camera ID'], 'Status': {}},
            'BacklightMode': {'Parameters': ['Camera ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Camera ID'], 'Status': {}},
            'DigitalZoom': {'Parameters': ['Camera ID'], 'Status': {}},
            'ExposureCompAmount': {'Parameters': ['Camera ID'], 'Status': {}},
            'ExposureCompensation': {'Parameters': ['Camera ID'], 'Status': {}},
            'Focus': {'Parameters': ['Camera ID', 'Speed'], 'Status': {}},
            'Gain': {'Parameters': ['Camera ID'], 'Status': {}},
            'HighResolution': {'Parameters': ['Camera ID'], 'Status': {}},
            'HighSensitivity': {'Parameters': ['Camera ID'], 'Status': {}},
            'Iris': {'Parameters': ['Camera ID'], 'Status': {}},
            'PanTilt': {'Parameters': ['Camera ID', 'Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PictureEffect': {'Parameters': ['Camera ID'], 'Status': {}},
            'Power': {'Parameters': ['Camera ID'], 'Status': {}},
            'Preset': {'Parameters': ['Camera ID', 'Action'], 'Status': {}},
            'Shutter': {'Parameters': ['Camera ID'], 'Status': {}},
            'WideDynamicRange': {'Parameters': ['Camera ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Camera ID', 'Speed'], 'Status': {}},
        }  

    def SetCamID(self, value):
        try:
            value = int(value)
            if 1 <= value <= 7:
                return 0x80 + value
        except ValueError:
            pass

        return 0
      
    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            ApertureCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
            self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAperture')
    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':    0x00,
            'Manual':       0x03,
            'Shutter':      0x0A,
            'Iris':         0x0B,
            'Bright':       0x0D
        }
        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            AutoExposureCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Full Auto',
            b'\x03': 'Manual',
            b'\x0A': 'Shutter',
            b'\x0B': 'Iris',
            b'\x0D': 'Bright'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            AutoExposureCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x39, 0xFF)
            res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('AutoExposure', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Auto Exposure: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAutoExposure')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            AutoFocusCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')
    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            AutoFocusCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x38, 0xFF)
            res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('AutoFocus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Auto Focus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAutoFocus')

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            BacklightModeCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightMode')
    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            BacklightModeCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x33, 0xFF)
            res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('BacklightMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Backlight Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBacklightMode')

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            BrightnessCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0D, ValueStateValues[value], 0xFF)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')
    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            DigitalZoomCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x06, ValueStateValues[value], 0xFF)
            self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalZoom')
    def UpdateDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            DigitalZoomCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x06, 0xFF)
            res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('DigitalZoom', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Digital Zoom: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDigitalZoom')

    def SetExposureCompAmount(self, value, qualifier):

        ValueStateValues = {
            'Reset':    0x00,
            'Up':       0x02,
            'Down':     0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            ExposureCompAmountCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0E, ValueStateValues[value], 0xFF)
            self.__SetHelper('ExposureCompAmount', ExposureCompAmountCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExposureCompAmount')
    def SetExposureCompensation(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            ExposureCompensationCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x3E, ValueStateValues[value], 0xFF)
            self.__SetHelper('ExposureCompensation', ExposureCompensationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExposureCompensation')
    def UpdateExposureCompensation(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            ExposureCompensationCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x3E, 0xFF)
            res = self.__UpdateHelper('ExposureCompensation', ExposureCompensationCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('ExposureCompensation', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Exposure Compensation: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateExposureCompensation')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far':  0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        FocusSpeed = int(qualifier['Speed'])

        if cameraID and 0 <= FocusSpeed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                FocusSpeed = 0x00
            else:
                FocusSpeed += ValueStateValues[value]

            FocusCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x08, FocusSpeed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            GainCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')
    def SetHighResolution(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            HighResolutionCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x52, ValueStateValues[value], 0xFF)
            self.__SetHelper('HighResolution', HighResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHighResolution')
    def UpdateHighResolution(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            HighResolutionCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x52, 0xFF)
            res = self.__UpdateHelper('HighResolution', HighResolutionCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('HighResolution', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['High Resolution: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateHighResolution')

    def SetHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            HighSensitivityCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x5E, ValueStateValues[value], 0xFF)
            self.__SetHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHighSensitivity')
    def UpdateHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            HighSensitivityCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x5E, 0xFF)
            res = self.__UpdateHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('HighSensitivity', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['High Sensitivity: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateHighSensitivity')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }
        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            IrisCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')
  
    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Stop':         0x0303,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Home':         0x04,
            'Reset':        0x05
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        PanSpeed = int(qualifier['Pan Speed'])
        TiltSpeed = int(qualifier['Tilt Speed'])

        if cameraID and 1 <= PanSpeed <= 24 and 1 <= TiltSpeed <= 20 and value in ValueStateValues:
            if value in ('Home', 'Reset'):
                PanTiltCmdString = pack('>5B', cameraID, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', cameraID, 0x01, 0x06, 0x01, PanSpeed, TiltSpeed, ValueStateValues[value], 0xFF) 

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')
    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Off':      0x00,
            'Negative': 0x02,
            'B&W':      0x04
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            PictureEffectCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
            self.__SetHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureEffect')
    def UpdatePictureEffect(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x02': 'Negative',
            b'\x04': 'B&W'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            PictureEffectCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x63, 0xFF)
            res = self.__UpdateHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('PictureEffect', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture Effect: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureEffect')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            PowerCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
    def UpdatePower(self, value, qualifier):


        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])

        if cameraID == self.CameraID:
            return

        if cameraID:
            PowerCmdString = pack('>5B', cameraID, 0x09, 0x04, 0x00, 0xFF)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save':     0x01,
            'Reset':    0x00,
            'Recall':   0x02
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        Action = qualifier['Action']
        value = int(value)

        if cameraID and 1 <= value <= 16 and Action in ActionStates:
            PresetCmdString = pack('>7B', cameraID, 0x01, 0x04, 0x3F, ActionStates[Action], value - 1, 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset':    0x00,
            'Up':       0x02,
            'Down':     0x03
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            ShutterCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')
    def SetWideDynamicRange(self, value, qualifier):

        ValueStateValues = {
            'Low':  0x01,
            'Mid':  0x02,
            'High': 0x03,
            'Off':  0x00
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID and value in ValueStateValues:
            WideDynamicRangeCmdString = pack('>7B', cameraID, 0x01, 0x7E, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('WideDynamicRange', WideDynamicRangeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWideDynamicRange')
    def UpdateWideDynamicRange(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Low',
            b'\x02': 'Mid',
            b'\x03': 'High',
            b'\x00': 'Off'
        }
        cameraID = self.SetCamID(qualifier['Camera ID'])
        if cameraID:
            WideDynamicRangeCmdString = pack('>6B', cameraID, 0x09, 0x7E, 0x04, 0x00, 0xFF)
            res = self.__UpdateHelper('WideDynamicRange', WideDynamicRangeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('WideDynamicRange', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Wide Dynamic Range: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateWideDynamicRange')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        cameraID = self.SetCamID(qualifier['Camera ID'])
        ZoomSpeed = int(qualifier['Speed'])

        if cameraID and 0 <= ZoomSpeed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                ZoomSpeed = 0x00
            else:
                ZoomSpeed += ValueStateValues[value]

            ZoomCmdString = pack('>6B', cameraID, 0x01, 0x04, 0x07, ZoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                Errors = {
                    0x01: 'Message Length Error',
                    0x02: 'Syntax Error',
                    0x03: 'Command Buffer Full',
                    0x04: 'Command Cancelled',
                    0x05: 'No Socket',
                    0x41: 'Command Not Executable',
                }

                address, errorbyte, errorcode, terminator = unpack('>4B', response)
                if errorbyte & 0x60 == 0x60:
                    self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, Errors.get(errorcode, 'Unknown Error'))])
                    response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
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

    Objects = {}

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self._ReceiveBuffer = b''
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Brightness': {'Status': {}},
            'DigitalZoom': {'Status': {}},
            'ExposureCompAmount': {'Status': {}},
            'ExposureCompensation': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': {'Status': {}},
            'HighResolution': {'Status': {}},
            'HighSensitivity': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PictureEffect': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Shutter': {'Status': {}},
            'WideDynamicRange': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }

        self.PrevSequence = 0
        self.StartSequence = 1
        self.LastResetTime = time.monotonic()

        self.LastCommand = None
        self.cmdBuffer = deque(())
        self.cmdBusy = False

        DeviceEthernetClass.Objects[self.IPAddress] = self

    @classmethod
    def StartDataDispatch(cls):
        cls.server = EthernetServerInterface(52381, 'UDP')
        
        @event(cls.server, 'ReceiveData')
        def handleData(client, data):
            try:
                Object = cls.Objects[client.IPAddress]
            except KeyError:
                print('Unknown Device: {}'.format(client.IPAddress))
            Object.ReceiveDataHandler(data)
            
        if cls.server.StartListen() != 'Listening':
            print('Port unavailable: 52381')

    def ResetSequence(self,):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def IncSequenceNumber(self):

        if self.StartSequence == 0:
           ctime = time.monotonic()
           if ctime - self.LastResetTime > 15:
               self.LastResetTime = time.monotonic()
               self.ResetSequence()
           self.PrevSequence = 1
           Sequence = b'\x00\x00\x00\x01'
        else:

            self.PrevSequence = self.PrevSequence + 1 if self.PrevSequence < 4294967295 else 0
            Sequence = pack('>L', self.PrevSequence)
        return(Sequence)

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
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        ApertureCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Shutter': 0x0A,
            'Iris': 0x0B,
            'Bright': 0x0D
        }

        AutoExposureCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):
        AutoExposureCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x39, 0xFF)
        self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def MatchAutoExposure(self, data, qualifier):
        
        ValueStateValues = {
            b'\x00': 'Full Auto',
            b'\x03': 'Manual',
            b'\x0A': 'Shutter',
            b'\x0B': 'Iris',
            b'\x0D': 'Bright'
        }

        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('AutoExposure', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['AutoExposure Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        AutoFocusCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x38, 0xFF)
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def MatchAutoFocus(self, data, qualifier):
        
        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('AutoFocus', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['AutoFocus Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightModeCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        BacklightModeCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x33, 0xFF)
        self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
    
    def MatchBacklightMode(self, data, qualifier):
        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('BacklightMode', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['BacklightMode Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03
        }

        BrightnessCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0D, ValueStateValues[value], 0xFF)
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        DigitalZoomCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x06, ValueStateValues[value], 0xFF)
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def UpdateDigitalZoom(self, value, qualifier):

        DigitalZoomCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x06, 0xFF)
        self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def MatchDigitalZoom(self, data, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('DigitalZoom', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['DigitalZoom Invalid/unexpected response'])

    def SetExposureCompAmount(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }

        ExposureCompAmountCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0E, ValueStateValues[value], 0xFF)
        self.__SetHelper('ExposureCompAmount', ExposureCompAmountCmdString, value, qualifier)

    def SetExposureCompensation(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03,
        }

        ExposureCompensationCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x3E, ValueStateValues[value], 0xFF)
        self.__SetHelper('ExposureCompensation', ExposureCompensationCmdString, value, qualifier)

    def UpdateExposureCompensation(self, value, qualifier):

        ExposureCompensationCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x3E, 0xFF)
        self.__UpdateHelper('ExposureCompensation', ExposureCompensationCmdString, value, qualifier)

    def MatchExposureCompensation(self, data, qualifier):
        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off',
        }
        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('ExposureCompensation', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['ExposureCompensation Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min': 0,
            'Max': 7
        }

        ValueStateValues = {
            'Far': 0x20,
            'Near': 0x30
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
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

        GainCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
        self.__SetHelper('Gain', GainCmdString, value, qualifier)

    def SetHighResolution(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        HighResolutionCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x52, ValueStateValues[value], 0xFF)
        self.__SetHelper('HighResolution', HighResolutionCmdString, value, qualifier)

    def UpdateHighResolution(self, value, qualifier):

        HighResolutionCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x52, 0xFF)
        self.__UpdateHelper('HighResolution', HighResolutionCmdString, value, qualifier)

    def MatchHighResolution(self, data, qualifier):
        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('HighResolution', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['HighResolution Invalid/unexpected response'])

    def SetHighSensitivity(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        HighSensitivityCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x5E, ValueStateValues[value], 0xFF)
        self.__SetHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)

    def UpdateHighSensitivity(self, value, qualifier):
        HighSensitivityCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x5E, 0xFF)
        self.__UpdateHelper('HighSensitivity', HighSensitivityCmdString, value, qualifier)

    def MatchHighSensitivity(self, data, qualifier):
        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('HighSensitivity', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['HighSensitivity Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        IrisCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

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
            'Up': (0x03, 0x01),
            'Down': (0x03, 0x02),
            'Left': (0x01, 0x03),
            'Right': (0x02, 0x03),
            'Stop': (0x03, 0x03),
            'Up Left': (0x01, 0x01),
            'Up Right': (0x02, 0x01),
            'Down Left': (0x01, 0x02),
            'Down Right': (0x02, 0x02),
            'Home': 0x04,
            'Reset': 0x05
        }

        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])

        if (PanSpeedConstraints['Min'] <= PanSpd <= PanSpeedConstraints['Max']) and (TiltSpeedConstraints['Min'] <= TiltSpd <= TiltSpeedConstraints['Max']):
            if value not in ('Home', 'Reset'):
                PanTiltCmdString = pack('>9B', 0x81, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            elif value in ('Home', 'Reset'):
                PanTiltCmdString = pack('>5B', 0x81, 0x01, 0x06, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Off': 0x00,
            'Negative': 0x02,
            'B&W': 0x04
        }

        PictureEffectCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
        self.__SetHelper('PictureEffect', PictureEffectCmdString, value, qualifier)

    def UpdatePictureEffect(self, value, qualifier):
        PictureEffectCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x63, 0xFF)
        self.__UpdateHelper('PictureEffect', PictureEffectCmdString, value, qualifier)

    def MatchPictureEffect(self, data, qualifier):
        ValueStateValues = {
            b'\x00': 'Off',
            b'\x02': 'Negative',
            b'\x04': 'B&W'
        }
        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('PictureEffect', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['PictureEffect Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        PowerCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x00, 0xFF)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def MatchPower(self, data, qualifier):
        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('Power', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Power Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': 0x01,
            'Reset': 0x00,
            'Recall': 0x02
        }

        if 0 <= int(value) <= 15:
            PresetCmdString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, ActionStates[qualifier['Action']], int(value), 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }

        ShutterCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetWideDynamicRange(self, value, qualifier):

        ValueStateValues = {
            'Low': 0x01,
            'Mid': 0x02,
            'High': 0x03,
            'Off': 0x00
        }

        WideDynamicRangeCmdString = pack('>7B', 0x81, 0x01, 0x7E, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('WideDynamicRange', WideDynamicRangeCmdString, value, qualifier)

    def UpdateWideDynamicRange(self, value, qualifier):
        WideDynamicRangeCmdString = pack('>6B', 0x81, 0x09, 0x7E, 0x04, 0x00, 0xFF)
        self.__UpdateHelper('WideDynamicRange', WideDynamicRangeCmdString, value, qualifier)
        
    def MatchWideDynamicRange(self, data, qualifier):
        ValueStateValues = {
            b'\x01': 'Low',
            b'\x02': 'Mid',
            b'\x03': 'High',
            b'\x00': 'Off'
        }
        try:
            value = ValueStateValues[data[2:3]]
            self.WriteStatus('WideDynamicRange', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['WideDynamicRange Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 0,
            'Max': 7
            }

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, response):
        if response:
            try:
                response = response[8:12] if len(response) == 12 else response 
                address, errorByte, errorCode, terminator = unpack('>4B', response)
                if (errorByte == 0x60) and (errorCode == 0x02):
                    self.Error(['Syntax Error'])
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x03):
                    self.Error(['Command Buffer Full'])
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x04):
                    self.Error(['Command Cancelled'])
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x05):
                    self.Error(['No Socket'])
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x41):
                    self.Error(['Command Not Executable'])
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x01):
                    self.Error(['Message length error'])
                    response = ''
            except:
                pass
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        newcommandstring = self.SetHeader(commandstring)
    
        if self.Unidirectional == 'True':
            self.Send(newcommandstring)
        else:
            self.__SendHelper(command, qualifier, newcommandstring, 'Set')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
        
        newcommandstring = self.GetHeader(commandstring)

        if self.Unidirectional == 'True':
            self.Send(newcommandstring)
        else:            
            self.__SendHelper(command, qualifier, newcommandstring, 'Update')

    def __SendHelper(self,command,qualifier=None,commandstring='',messageType=''):
        self.cmdBuffer.append((command,qualifier,commandstring, messageType))
        self.__ProcessSend()

    def __ProcessSend(self):
        '''
        If we are not waiting for a response (self.cmdBusy flag is free (False))
        '''        
        if(not self.cmdBusy and len(self.cmdBuffer) > 0):                
            self.cmdBusy = True
            #Set cmdWait timer to check for connection loss
            try:
                self._cmdWait.Restart()
            except AttributeError:
                self._cmdWait = Wait(1,self.ResponseCheck) 
            try:
                self.LastCommand =  self.cmdBuffer.popleft()
            except:
                self.cmdBusy = False
                self._cmdWait.Cancel()
                self.LastCommand = None
                self.counter = 0
            else:
                try:
                    self.Send(self.LastCommand[2])
                except:
                    pass

    def ResponseCheck(self):
        '''
        Checks for a response for the last command sent out (Set or Update)
        '''
        if (self.cmdBusy):
            self.cmdBusy = False
            if(self.connectionFlag):
                self.counter += 1
                if (self.counter > self.connectionCounter):
                    self.counter = 0
                    self.OnDisconnected()  
            else:
                self.cmdBuffer.clear()   

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.cmdBusy = False
        self.ResetSequence()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.StartSequence = 0
        
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

    def ReceiveDataHandler(self, data): 
        data = self.__CheckResponseForErrors(data)
        if data:
            if(self.LastCommand):
                command, qualifier, cmdString, messageType = self.LastCommand
                if(self._cmdWait):
                    self._cmdWait.Cancel()
                if messageType == 'Update':
                    try:
                        getattr(self, 'Match%s' % command)(data, qualifier)
                    except AttributeError:
                        print(command, 'does not support Match.')

                # Response recevied. Kill wait and call next command in the buffer
                self.cmdBusy = False
                self.LastCommand = None
                self.counter = 0                
                self.__ProcessSend()  

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model=None):
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
