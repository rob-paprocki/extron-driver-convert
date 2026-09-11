from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
            'AudioMicVolume': { 'Status': {}},
            'AudioOutVolume': { 'Status': {}},
            'AutoErase': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'CaptureAction': { 'Status': {}},
            'CaptureInterval': { 'Status': {}},
            'CaptureTime': { 'Status': {}},
            'Delete': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Function': { 'Status': {}},
            'GammaMode': { 'Status': {}},
            'ImageMode': { 'Status': {}},
            'ImageQuality': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'Lamp': { 'Status': {}},
            'MaskMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MenuStatus': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PanMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'SlideShow': { 'Status': {}},
            'SlideShowDelay': { 'Status': {}},
            'SourceLive': {'Parameters':['VGA Out 1','VGA Out 2'], 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }




    def SetAudioMicVolume(self, value, qualifier):

        if 0 <= value <= 16:
            AudioMicVolumeCmdString =  b''.join([b'\xA0\xD4', bytes([value]), b'\x00\x00\xAF'])
            self.__SetHelper('AudioMicVolume', AudioMicVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMicVolume')
    def UpdateAudioMicVolume(self, value, qualifier):

        AudioMicVolumeCmdString = b'\xA0\xD5\x00\x00\x00\xAF'
        res = self.__UpdateHelper('AudioMicVolume', AudioMicVolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[2]
                self.WriteStatus('AudioMicVolume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Audio Mic Volume: Invalid/unexpected response'])

    def SetAudioOutVolume(self, value, qualifier):

        if 0 <= value <= 31:
            AudioOutVolumeCmdString = b''.join([b'\xA0\xD6', bytes([value]), b'\x00\x00\xAF'])
            self.__SetHelper('AudioOutVolume', AudioOutVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutVolume')
    def UpdateAudioOutVolume(self, value, qualifier):

        AudioOutVolumeCmdString = b'\xA0\xD7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('AudioOutVolume', AudioOutVolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[2]
                self.WriteStatus('AudioOutVolume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Audio Out Volume: Invalid/unexpected response'])

    def SetAutoErase(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\x14\x01\x00\x00\xAF', 
            'Off' : b'\xA0\x14\x00\x00\x00\xAF'
        }

        AutoEraseCmdString = ValueStateValues[value]
        self.__SetHelper('AutoErase', AutoEraseCmdString, value, qualifier)


    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 105:
            BrightnessCmdString = b''.join([b'\xA0\x30\x01', bytes([value]), b'\x00\xAF'])
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')
    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = b'\xA0\x89\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = res[2]
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetCaptureAction(self, value, qualifier):

        ValueStateValues = {
            'Single Capture' : b'\xA0\x96\x00\x00\x00\xAF', 
            'Time Lapse'     : b'\xA0\x96\x01\x00\x00\xAF', 
            'Record'         : b'\xA0\x96\x02\x00\x00\xAF', 
            'Disabled'       : b'\xA0\x96\x03\x00\x00\xAF'
        }

        CaptureActionCmdString = ValueStateValues[value]
        self.__SetHelper('CaptureAction', CaptureActionCmdString, value, qualifier)


    def SetCaptureInterval(self, value, qualifier):

        ValueStateValues = {
            '3 sec'  : b'\xA0\x98\x00\x00\x00\xAF', 
            '5 sec'  : b'\xA0\x98\x01\x00\x00\xAF', 
            '10 sec' : b'\xA0\x98\x02\x00\x00\xAF', 
            '30 sec' : b'\xA0\x98\x03\x00\x00\xAF', 
            '1 min'  : b'\xA0\x98\x04\x00\x00\xAF', 
            '2 min'  : b'\xA0\x98\x05\x00\x00\xAF', 
            '5 min'  : b'\xA0\x98\x06\x00\x00\xAF'
        }

        CaptureIntervalCmdString = ValueStateValues[value]
        self.__SetHelper('CaptureInterval', CaptureIntervalCmdString, value, qualifier)


    def SetCaptureTime(self, value, qualifier):

        ValueStateValues = {
            '1 hr'  : b'\xA0\x97\x00\x00\x00\xAF', 
            '2 hr'  : b'\xA0\x97\x01\x00\x00\xAF', 
            '4 hr'  : b'\xA0\x97\x02\x00\x00\xAF', 
            '8 hr'  : b'\xA0\x97\x03\x00\x00\xAF', 
            '24 hr' : b'\xA0\x97\x04\x00\x00\xAF', 
            '48 hr' : b'\xA0\x97\x05\x00\x00\xAF', 
            '72 hr' : b'\xA0\x97\x06\x00\x00\xAF'
        }

        CaptureTimeCmdString = ValueStateValues[value]
        self.__SetHelper('CaptureTime', CaptureTimeCmdString, value, qualifier)


    def SetDelete(self, value, qualifier):

        ValueStateValues = {
            'Delete One' : b'\xA0\xB6\x00\x00\x00\xAF', 
            'Delete All' : b'\xA0\xB6\x01\x00\x00\xAF', 
            'Format'     : b'\xA0\xB6\x02\x00\x00\xAF'
        }

        DeleteCmdString = ValueStateValues[value]
        self.__SetHelper('Delete', DeleteCmdString, value, qualifier)


    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'  : b'\xA0\x1A\x01', 
            'Near' : b'\xA0\x1A\x00', 
            'Stop' : b'\xA0\x19\x00\x00\x00\xAF'
        }

        speed = int(qualifier['Speed'])
        if 0 <= speed <= 6:
            if value == 'Stop':
                FocusCmdString = ValueStateValues[value]
            else:
                FocusCmdString = b''.join([ValueStateValues[value], bytes([speed]), b'\x00\xAF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')


    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\x2C\x01\x00\x00\xAF', 
            'Off' : b'\xA0\x2C\x00\x00\x00\xAF'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetFunction(self, value, qualifier):

        ValueStateValues = {
            'AF One Push Trigger' : b'\xA0\xA3\x01\x00\x00\xAF', 
            'AWB Correction'      : b'\xA0\x56\x00\x00\x00\xAF', 
            'Capture'             : b'\xA0\xB2\x00\x00\x00\xAF', 
            'Copy to USB'         : b'\xA0\x08\x00\x00\x00\xAF', 
            'Factory Reset'       : b'\xA0\x03\x01\x00\x00\xAF', 
            'Playback Thumbnail'  : b'\xA0\xB3\x00\x00\x00\xAF', 
            'Record'              : b'\xA0\xB2\x01\x00\x00\xAF'
        }

        FunctionCmdString = ValueStateValues[value]
        self.__SetHelper('Function', FunctionCmdString, value, qualifier)


    def SetGammaMode(self, value, qualifier):

        ValueStateValues = {
            'Photo' : b'\xA0\xA7\x00\x00\x00\xAF', 
            'Text'  : b'\xA0\xA7\x01\x00\x00\xAF', 
            'Gray'  : b'\xA0\xA7\x02\x00\x00\xAF'
        }

        GammaModeCmdString = ValueStateValues[value]
        self.__SetHelper('GammaMode', GammaModeCmdString, value, qualifier)
    def UpdateGammaMode(self, value, qualifier):

        ValueStateValues = {
            0 : 'Photo', 
            1 : 'Text', 
            2 : 'Gray'
        }

        GammaModeCmdString =  b'\xA0\x51\x00\x00\x00\xAF'
        res = self.__UpdateHelper('GammaMode', GammaModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('GammaMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Gamma Mode: Invalid/unexpected response'])

    def SetImageMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'     : b'\xA0\xA9\x00\x00\x00\xAF', 
            'Slide'      : b'\xA0\xA9\x01\x00\x00\xAF', 
            'Film'       : b'\xA0\xA9\x02\x00\x00\xAF', 
            'Microscope' : b'\xA0\xA9\x00\x03\x00\xAF'
        }

        ImageModeCmdString = ValueStateValues[value]
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)


    def SetImageQuality(self, value, qualifier):

        ValueStateValues = {
            'High'   : b'\xA0\x07\x00\x00\x00\xAF', 
            'Medium' : b'\xA0\x07\x01\x00\x00\xAF', 
            'Low'    : b'\xA0\x07\x02\x00\x00\xAF'
        }

        ImageQualityCmdString = ValueStateValues[value]
        self.__SetHelper('ImageQuality', ImageQualityCmdString, value, qualifier)


    def SetImageRotation(self, value, qualifier):

        ValueStateValues = {
            '0'      : b'\xA0\xB4\x00\x00\x00\xAF', 
            '180'    : b'\xA0\xB4\x01\x00\x00\xAF', 
            'Flip'   : b'\xA0\xB4\x02\x00\x00\xAF', 
            'Mirror' : b'\xA0\xB4\x03\x00\x00\xAF'
        }

        ImageRotationCmdString = ValueStateValues[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)


    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'Lamp and Backlight Off' : b'\xA0\xC1\x00\x00\x00\xAF', 
            'Lamp On'                : b'\xA0\xC1\x01\x00\x00\xAF', 
            'Backlight On'           : b'\xA0\xC1\x02\x00\x00\xAF'
        }

        LampCmdString = ValueStateValues[value]
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)
    def UpdateLamp(self, value, qualifier):

        ValueStateValues = {
            0 : 'Lamp and Backlight Off', 
            1 : 'Lamp On', 
            2 : 'Backlight On'
        }

        LampCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp: Invalid/unexpected response'])

    def SetMaskMode(self, value, qualifier):

        ValueStateValues = {
            'Disable'   : b'\xA0\x27\x00\x00\x00\xAF', 
            'Mask'      : b'\xA0\x27\x01\x00\x00\xAF', 
            'Spotlight' : b'\xA0\x27\x02\x00\x00\xAF'
        }

        MaskModeCmdString = ValueStateValues[value]
        self.__SetHelper('MaskMode', MaskModeCmdString, value, qualifier)


    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\xA0\xA0\x02\x00\x00\xAF', 
            'Down'      : b'\xA0\xA0\x03\x00\x00\xAF', 
            'Left'      : b'\xA0\xA0\x04\x00\x00\xAF', 
            'Right'     : b'\xA0\xA0\x05\x00\x00\xAF', 
            'Menu'      : b'\xA0\xA0\x06\x00\x00\xAF', 
            'Enter'     : b'\xA0\xA0\x01\x00\x00\xAF', 
            'Page Up'   : b'\xA0\x4A\x01\x00\x00\xAF', 
            'Page Down' : b'\xA0\x4A\x00\x00\x00\xAF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def UpdateMenuStatus(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        MenuStatusCmdString = b'\xA0\x8B\x00\x00\x00\xAF'
        res = self.__UpdateHelper('MenuStatus', MenuStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('MenuStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Menu Status: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\x4B\x01\x00\x00\xAF', 
            'Off' : b'\xA0\x4B\x00\x00\x00\xAF'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)


    def SetPanMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\x26\x01\x00\x00\xAF', 
            'Off' : b'\xA0\x26\x00\x00\x00\xAF'
        }

        PanModeCmdString = ValueStateValues[value]
        self.__SetHelper('PanMode', PanModeCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\xB1\x01\x00\x00\xAF', 
            'Off' : b'\xA0\xB1\x00\x00\x00\xAF', 
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off', 
        }

        PowerCmdString = b'\xA0\xB7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if res[2] == 0:
                    value = 'Not Ready'
                elif res[2] == 1:
                    value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = b'\xA0\x03\x00\x00\x00\xAF'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)


    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = b'\xA0\x03\x00\x01\x00\xAF'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)


    def SetSlideShow(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\x04\x01\x00\x00\xAF', 
            'Off' : b'\xA0\x04\x00\x00\x00\xAF'
        }

        SlideShowCmdString = ValueStateValues[value]
        self.__SetHelper('SlideShow', SlideShowCmdString, value, qualifier)


    def SetSlideShowDelay(self, value, qualifier):

        ValueStateValues = {
            '0.5 sec'  : b'\xA0\x06\x00\x00\x00\xAF', 
            '1.0 sec'  : b'\xA0\x06\x01\x00\x00\xAF', 
            '3.0 sec'  : b'\xA0\x06\x02\x00\x00\xAF', 
            '5.0 sec'  : b'\xA0\x06\x03\x00\x00\xAF', 
            '10.0 sec' : b'\xA0\x06\x04\x00\x00\xAF', 
            'Manual'   : b'\xA0\x06\x05\x00\x00\xAF'
        }

        SlideShowDelayCmdString = ValueStateValues[value]
        self.__SetHelper('SlideShowDelay', SlideShowDelayCmdString, value, qualifier)


    def SetSourceLive(self, value, qualifier):

        States = {
            'Camera' : b'\x00', 
            'PC'     : b'\x01', 
            'Off'    : b'\x02'
        }

        VGA1 = qualifier['VGA Out 1']
        VGA2 = qualifier['VGA Out 2']
        if VGA1 in States and VGA2 in States:
            SourceLiveCmdString =  b''.join([b'\xA0\x3A', States[VGA1], States[VGA2], b'\x00\xAF'])
            self.__SetHelper('SourceLive', SourceLiveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSourceLive')


    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto Tune' : b'\xA0\x22\x00\x00\x00\xAF', 
            'AWB'       : b'\xA0\x22\x01\x00\x00\xAF'
        }

        WhiteBalanceCmdString = ValueStateValues[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)


    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : b'\xA0\x11\x00\x00\x00\xAF', 
            'Wide' : b'\xA0\x11\x01\x00\x00\xAF', 
            'Stop' : b'\xA0\x10\x00\x00\x00\xAF'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)


    def __CheckResponseForErrors(self, sourceCmdName, response):



        res = response[-2]
        error_states = {1:'NAK (No Action)', 2:'Ignore (Command is not in the command list)'}
        if response:
            if res in error_states:
                self.Error(['{0}:{1}'.format(sourceCmdName, error_states[res])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True




        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
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

