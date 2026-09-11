from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
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
        
        self.DeviceIDStates = {
                '1' : 1, 
                '2' : 2, 
                '3' : 3, 
                '4' : 4, 
                '5' : 5, 
                '6' : 6, 
                '7' : 7, 
                '8' : 8, 
                '9' : 9, 
                'A' : 10, 
                'B' : 11, 
                'C' : 12, 
                'D' : 13, 
                'E' : 14, 
                'F' : 15
            }
            
        self.DeviceID = '1'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture': { 'Status': {}},
            'AutoExposure': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'DigitalZoom': { 'Status': {}},
            'Focus': { 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Gain': { 'Status': {}},
            'Home': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'PictureFlip': { 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'RemoteControlLock': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }




        
            

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value in self.DeviceIDStates:
            self._DeviceID = 0x80 + self.DeviceIDStates[value]
        else:
            self.Error(['Device ID Out of Range']) 
    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        ApertureCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF])
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)
    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'         : 0x00, 
            'Manual'            : 0x03, 
            'Shutter Priority'  : 0x0A, 
            'Iris Priority'     : 0x0B, 
            'Bright'            : 0x0D
        }

        AutoExposureCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF])
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Full Auto', 
            0x03 : 'Manual', 
            0x0A : 'Shutter Priority', 
            0x0B : 'Iris Priority', 
            0x0D : 'Bright'
        }

        AutoExposureCmdString = bytes([self.DeviceID, 0x09, 0x04, 0x39, 0xFF])
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        BacklightCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF])
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        BacklightCmdString = bytes([self.DeviceID, 0x09, 0x04, 0x33, 0xFF])
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 0x02, 
            'Down' : 0x03
        }

        BrightnessCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x0D, ValueStateValues[value], 0xFF])
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        DigitalZoomCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x06, ValueStateValues[value], 0xFF])
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def UpdateDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        DigitalZoomCmdString = bytes([self.DeviceID, 0x09, 0x04, 0x06, 0xFF])
        res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('DigitalZoom', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Digital Zoom: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'  : 0x02, 
            'Near' : 0x03, 
            'Stop' : 0x00
        }

        FocusCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : 0x02, 
            'Manual' : 0x03
        }

        FocusModeCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF])
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'Auto', 
            0x03 : 'Manual'
        }

        FocusModeCmdString = bytes([self.DeviceID, 0x09, 0x04, 0x38, 0xFF])
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        GainCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF])
        self.__SetHelper('Gain', GainCmdString, value, qualifier)
    def SetHome(self, value, qualifier):

        HomeCmdString = bytes([self.DeviceID, 0x01, 0x06, 0x04, 0xFF])
        self.__SetHelper('Home', HomeCmdString, value, qualifier)
    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        IrisCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF])
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)
    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : [0x03, 0x01], 
            'Down'       : [0x03, 0x02], 
            'Left'       : [0x01, 0x03], 
            'Right'      : [0x02, 0x03], 
            'Up Left'    : [0x01, 0x01], 
            'Up Right'   : [0x02, 0x01], 
            'Down Left'  : [0x01, 0x02], 
            'Down Right' : [0x02, 0x02], 
            'Stop'       : [0x03, 0x03]
        }

        panspeed = int(qualifier['Pan Speed'])
        tiltspeed = int(qualifier['Tilt Speed'])
        if 1<=panspeed<=18 and 1<=tiltspeed<=17:
            PanTiltCmdString = bytes([self.DeviceID, 0x01, 0x06, 0x01, panspeed, tiltspeed, ValueStateValues[value][0],ValueStateValues[value][1], 0xFF])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')
    def SetPictureFlip(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        PictureFlipCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x66, ValueStateValues[value], 0xFF])
        self.__SetHelper('PictureFlip', PictureFlipCmdString, value, qualifier)

    def UpdatePictureFlip(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        PictureFlipCmdString = bytes([self.DeviceID, 0x09, 0x04, 0x66, 0xFF])
        res = self.__UpdateHelper('PictureFlip', PictureFlipCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PictureFlip', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Flip: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        PowerCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        PowerCmdString = bytes([self.DeviceID, 0x09, 0x04, 0x00, 0xFF])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Recall' : 0x02, 
            'Reset'  : 0x00, 
            'Save'   : 0x01
        }

        action = qualifier['Action']
        if action in ActionStates and 1 <= int(value) <= 256:
            PresetCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x3F, ActionStates[action], int(value)-1, 0xFF])
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x03, 
            'Off' : 0x02
        }

        RemoteControlLockCmdString = bytes([self.DeviceID, 0x01, 0x06, 0x08, ValueStateValues[value], 0xFF])
        self.__SetHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)

    def UpdateRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            0x03 : 'On', 
            0x02 : 'Off'
        }

        RemoteControlLockCmdString = bytes([self.DeviceID, 0x09, 0x06, 0x08, 0xFF])
        res = self.__UpdateHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('RemoteControlLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Remote Control Lock: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        ShutterCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto'        : 0x00, 
            'Indoor'      : 0x01, 
            'Outdoor'     : 0x02, 
            'One Push WB' : 0x03, 
            'ATW'         : 0x04, 
            'Manual'      : 0x05
        }

        WhiteBalanceCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF])
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Auto', 
            0x01 : 'Indoor', 
            0x02 : 'Outdoor', 
            0x03 : 'One Push WB', 
            0x04 : 'ATW', 
            0x05 : 'Manual'
        }

        WhiteBalanceCmdString = bytes([self.DeviceID, 0x09, 0x04, 0x35, 0xFF])
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x02, 
            'Wide' : 0x03, 
            'Stop' : 0x00
        }

        ZoomCmdString = bytes([self.DeviceID, 0x01, 0x04, 0x07, ValueStateValues[value], 0xFF])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

