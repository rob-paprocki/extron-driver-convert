from extronlib.interface import (EthernetClientInterface, EthernetServerInterfaceEx, SerialInterface)
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
        self.Models = {}
        self._CameraID = 0x81
        self.Commands = {
            'Aperture': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Brightness': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'ExposureCompAmount': {'Status': {}},
            'ExposureCompensation': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PictureEffect': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Shutter': {'Status': {}},
            'Tracking': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }

    @property
    def CameraID(self):
        return self._CameraID

    @CameraID.setter
    def CameraID(self, value):
        if 1 <= int(value) <= 7:
            self._CameraID = 0x80 + int(value)
        else:
            print('Invalid CameraID value. Range is from 1 to 7')

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        ApertureCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)


    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto' : 0x00,
            'Manual'    : 0x03,
            'Shutter'   : 0x0A,
            'Iris'      : 0x0B,
            'Bright'    : 0x0D
        }

        AutoExposureCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Full Auto', 
            b'\x03' : 'Manual', 
            b'\x0A' : 'Shutter', 
            b'\x0B' : 'Iris', 
            b'\x0D' : 'Bright'
        }

        AutoExposureCmdString = pack('>5B', self._CameraID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        AutoFocusCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x38,ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }

        AutoFocusCmdString = pack('>5B', self._CameraID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        BacklightCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }

        BacklightCmdString = pack('>5B', self._CameraID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 0x02, 
            'Down' : 0x03
        }

        BrightnessCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0D, ValueStateValues[value], 0xFF)
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)


    def SetExposureCompAmount(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        ExposureCompAmountCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0E, ValueStateValues[value], 0xFF)
        self.__SetHelper('ExposureCompAmount', ExposureCompAmountCmdString, value, qualifier)
        

    def SetExposureCompensation(self, value, qualifier):

        ValueStateValues = {
            'On'    : 0x02, 
            'Off'   : 0x03, 
        }             

        ExposureCompensationCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x3E, ValueStateValues[value], 0xFF)
        self.__SetHelper('ExposureCompensation', ExposureCompensationCmdString, value, qualifier)

    def UpdateExposureCompensation(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off', 
        }

        ExposureCompensationCmdString = pack('>5B', self._CameraID, 0x09, 0x04, 0x3E, 0xFF)
        res = self.__UpdateHelper('ExposureCompensation', ExposureCompensationCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('ExposureCompensation', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Exposure compensation: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ValueStateValues = {
            'Far'  : 0x20, 
            'Near' : 0x30 
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
            FocusCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')


    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03,
            'Reset' : 0x00
        }

        GainCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
        self.__SetHelper('Gain', GainCmdString, value, qualifier)
            

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03,
            'Reset' : 0x00
        }

        IrisCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)


    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min' : 1,
            'Max' : 24
            }

        TiltSpeedConstraints = {
            'Min' : 1,
            'Max' : 20
            }

        ValueStateValues = {
            'Up'         : (0x03,0x01), 
            'Down'       : (0x03,0x02), 
            'Left'       : (0x01,0x03), 
            'Right'      : (0x02,0x03), 
            'Stop'       : (0x03,0x03), 
            'Up Left'    : (0x01,0x01),
            'Up Right'   : (0x02,0x01),
            'Down Left'  : (0x01,0x02),
            'Down Right' : (0x02,0x02),
            'Home'       : 0x04, 
            'Reset'      : 0x05
        }

        PanSpd  = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])

        if (PanSpeedConstraints['Min'] <= PanSpd <= PanSpeedConstraints['Max']) and (TiltSpeedConstraints['Min'] <= TiltSpd <= TiltSpeedConstraints['Max']):
            if value not in ('Home','Reset'):          
                PanTiltCmdString = pack('>9B', self._CameraID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0],ValueStateValues[value][1], 0xFF)
            elif value in ('Home','Reset'): 
                PanTiltCmdString = pack('>5B', self._CameraID, 0x01, 0x06, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')            


    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Off'      : 0x00, 
            'Negative Art' : 0x02, 
            'Black And White'      : 0x04
        }

        PictureEffectCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
        self.__SetHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
    def UpdatePictureEffect(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Off', 
            b'\x02' : 'Negative Art', 
            b'\x04' : 'Black And White'
        }

        PictureEffectCmdString = pack('>5B', self._CameraID, 0x09, 0x04, 0x63, 0xFF)
        res = self.__UpdateHelper('PictureEffect', PictureEffectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('PictureEffect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Effect: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        PowerCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }

        PowerCmdString = pack('>5B', self._CameraID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save'   : 0x01, 
            'Reset'  : 0x00, 
            'Recall' : 0x02
        }
        
        if 0 <= int(value) <= 15:
            PresetCmdString = pack('>7B', self._CameraID, 0x01, 0x04, 0x3F, ActionStates[qualifier['Action']], int(value), 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')


    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        ShutterCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)


    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'Start' : 0x50, 
            'Stop'  : 0x51
        }

        TrackingCmdString = pack('>7B', self._CameraID, 0x01, 0x04, 0x3F, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Tracking', TrackingCmdString, value, qualifier)


    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto' : b'\x35\x00', 
            'Indoor' : b'\x35\x01', 
            'Outdoor' : b'\x35\x02', 
            'One Push' : b'\x35\x03', 
            'Manual' : b'\x35\x05', 
            'One Push Trigger' : b'\x10\x05'
        }

        WhiteBalanceCmdString = b'\x81\x01\x04' + ValueStateValues[value] + b'\xff'
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0 : 'Auto', 
            1 : 'Indoor', 
            2 : 'Outdoor', 
            3 : 'One Push', 
            5 : 'Manual'
        }

        WhiteBalanceCmdString = b'\x81\x09\x04\x35\xff'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
            }

        ValueStateValues = {
            'Tele' : 0x20, 
            'Wide' : 0x30  
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomCmdString =  pack('>6B', self._CameraID, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')


    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>4B', response)
                
                if (errorByte & 0x60 == 0x60) and ( errorCode == 0x02 ):
                    self.Error([sourceCmdName + ' Syntax Error'])
                    response = ''
                elif (errorByte & 0x60 == 0x60) and ( errorCode == 0x03 ):
                    self.Error([sourceCmdName + ' Command Buffer Full'])
                    response = ''
                elif (errorByte & 0x60 == 0x60) and ( errorCode == 0x04 ):
                    self.Error([sourceCmdName + ' Command Cancelled'])
                    response = ''
                elif (errorByte & 0x60 == 0x60) and ( errorCode == 0x05 ):
                    self.Error([sourceCmdName + ' No Socket'])
                    response = ''
                elif (errorByte & 0x60 == 0x60) and ( errorCode == 0x41 ):
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
                self.Error(['Unexpected/Invalid response'])
            else:
                res = self.__CheckResponseForErrors(command + ':' , res)                

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
                return self.__CheckResponseForErrors(command + ':' , res)                    
            
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
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self._CameraID = 0x81

        self.Commands = {
            'Aperture': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Brightness': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'ExposureCompAmount': {'Status': {}},
            'ExposureCompensation': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PictureEffect': {'Status': {}},
            'PowerOff': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Shutter': {'Status': {}},
            'Tracking': {'Status': {}},
            'UserDefinedCommand': {'Status': {}},
            'UserDefinedString': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }


    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        ApertureCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)


    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto' : 0x00,
            'Manual'    : 0x03,
            'Shutter'   : 0x0A,
            'Iris'      : 0x0B,
            'Bright'    : 0x0D
        }

        AutoExposureCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)


    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        AutoFocusCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x38,ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)


    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        BacklightCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)


    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 0x02, 
            'Down' : 0x03
        }

        BrightnessCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0D, ValueStateValues[value], 0xFF)
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)


    def SetExposureCompAmount(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        ExposureCompAmountCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0E, ValueStateValues[value], 0xFF)
        self.__SetHelper('ExposureCompAmount', ExposureCompAmountCmdString, value, qualifier)
        

    def SetExposureCompensation(self, value, qualifier):

        ValueStateValues = {
            'On'    : 0x02, 
            'Off'   : 0x03, 
        }             

        ExposureCompensationCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x3E, ValueStateValues[value], 0xFF)
        self.__SetHelper('ExposureCompensation', ExposureCompensationCmdString, value, qualifier)


    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ValueStateValues = {
            'Far'  : 0x20, 
            'Near' : 0x30 
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
            FocusCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')


    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03,
            'Reset' : 0x00
        }

        GainCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
        self.__SetHelper('Gain', GainCmdString, value, qualifier)
            

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03,
            'Reset' : 0x00
        }

        IrisCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)


    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min' : 1,
            'Max' : 24
            }

        TiltSpeedConstraints = {
            'Min' : 1,
            'Max' : 20
            }

        ValueStateValues = {
            'Up'         : (0x03,0x01), 
            'Down'       : (0x03,0x02), 
            'Left'       : (0x01,0x03), 
            'Right'      : (0x02,0x03), 
            'Stop'       : (0x03,0x03), 
            'Up Left'    : (0x01,0x01),
            'Up Right'   : (0x02,0x01),
            'Down Left'  : (0x01,0x02),
            'Down Right' : (0x02,0x02),
            'Home'       : 0x04, 
            'Reset'      : 0x05
        }

        PanSpd  = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])

        if (PanSpeedConstraints['Min'] <= PanSpd <= PanSpeedConstraints['Max']) and (TiltSpeedConstraints['Min'] <= TiltSpd <= TiltSpeedConstraints['Max']):
            if value not in ('Home','Reset'):          
                PanTiltCmdString = pack('>9B', self._CameraID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0],ValueStateValues[value][1], 0xFF)
            elif value in ('Home','Reset'): 
                PanTiltCmdString = pack('>5B', self._CameraID, 0x01, 0x06, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')            


    def SetPictureEffect(self, value, qualifier):

        ValueStateValues = {
            'Off'               : 0x00, 
            'Negative Art'      : 0x02, 
            'Black And White'   : 0x04
        }

        PictureEffectCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x63, ValueStateValues[value], 0xFF)
        self.__SetHelper('PictureEffect', PictureEffectCmdString, value, qualifier)


    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x00, 0x03, 0xFF)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)


    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save'   : 0x01, 
            'Reset'  : 0x00, 
            'Recall' : 0x02
        }
        
        if 0 <= int(value) <= 15:
            PresetCmdString = pack('>7B', self._CameraID, 0x01, 0x04, 0x3F, ActionStates[qualifier['Action']], int(value), 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')


    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        ShutterCmdString = pack('>6B', self._CameraID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)


    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'Start' : 0x50, 
            'Stop'  : 0x51
        }

        TrackingCmdString = pack('>7B', self._CameraID, 0x01, 0x04, 0x3F, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Tracking', TrackingCmdString, value, qualifier)


    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto' : b'\x35\x00', 
            'Indoor' : b'\x35\x01', 
            'Outdoor' : b'\x35\x02', 
            'One Push' : b'\x35\x03', 
            'Manual' : b'\x35\x05', 
            'One Push Trigger' : b'\x10\x05'
        }

        WhiteBalanceCmdString = b'\x81\x01\x04' + ValueStateValues[value] + b'\xff'
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)


    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
            }

        ValueStateValues = {
            'Tele' : 0x20, 
            'Wide' : 0x30  
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomCmdString =  pack('>6B', self._CameraID, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')


    def __CheckResponseForErrors(self, sourceCmdName, response):

        pass

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)       

    
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
