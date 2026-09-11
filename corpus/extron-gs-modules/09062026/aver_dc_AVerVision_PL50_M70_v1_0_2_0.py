from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

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
        self.Models = {
            'AVerVision PL50': self.aver_16_378_PL50,
            'AVerVision M70': self.aver_16_378_M70,
            }
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Contrast': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'Effect': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Format': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageCapture': { 'Status': {}},
            'Lamp': { 'Status': {}},
            'LightBox': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mirror': { 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'PreviewMode': { 'Status': {}},
            'Record': { 'Status': {}},
            'Rotate': { 'Status': {}},
            'SpotLightControl': { 'Status': {}},
            'SpotlightShade': { 'Status': {}},
            'Storage': { 'Status': {}},
            'VideoOutputStatus': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x36\x01\x00\x53\x6C',
            'Off': b'\x52\x0B\x03\x36\x00\x00\x53\x6D',
        }

        AutoImageCmdString = ValueStateValues[value]
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CKS = value ^ 0x4B
            BrightnessCmdString = pack('>8B', 0x52, 0x0B, 0x03, 0x12, 0x02, value, 0x53, CKS)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')
    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = b'\x52\x0A\x01\x0A\x53\x52'
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                self.WriteStatus('Brightness', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CKS = value ^ 0x48
            ContrastCmdString = pack('>8B', 0x52, 0x0B, 0x03, 0x11, 0x02, value, 0x53, CKS)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')
    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = b'\x52\x0A\x01\x0B\x53\x53'
        res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                self.WriteStatus('Contrast', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Contrast: Invalid/unexpected response'])

    def SetDisplayMode(self, value, qualifier):

        DisplayModeCmdString = self.DisplayModeValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
    def UpdateDisplayMode(self, value, qualifier):

        DisplayModeCmdString = b'\x52\x0A\x01\x06\x53\x5E'
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = self.DisplayModeSates[res[3]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Mode: Invalid/unexpected response'])

    def SetEffect(self, value, qualifier):

        ValueStateValues = {
            'Color':    b'\x52\x0B\x03\x10\x00\x00\x53\x4B',
            'B/W':      b'\x52\x0B\x03\x10\x01\x00\x53\x4A',
            'Negative': b'\x52\x0B\x03\x10\x02\x00\x53\x49',
        }

        EffectCmdString = ValueStateValues[value]
        self.__SetHelper('Effect', EffectCmdString, value, qualifier)
    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': b'\x52\x0B\x03\x48\x00\x00\x53\x13',
            'Far':  b'\x52\x0B\x03\x48\x01\x00\x53\x12',
            'Auto': b'\x52\x0B\x03\x40\x00\x00\x53\x1B',
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
    def SetFormat(self, value, qualifier):

        ValueStateValues = {
            'Embedded':    b'\x52\x0B\x03\x29\x00\x00\x53\x72',
            'SD':          b'\x52\x0B\x03\x29\x01\x00\x53\x73',
            'Flash Drive': b'\x52\x0B\x03\x29\x02\x00\x53\x70',
        }

        FormatCmdString = ValueStateValues[value]
        self.__SetHelper('Format', FormatCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):


        FreezeCmdString = b'\x52\x0B\x03\x44\x00\x00\x53\x1F'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off',
        }

        FreezeCmdString = b'\x52\x0A\x01\x08\x53\x50'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetImageCapture(self, value, qualifier):

        ValueStateValues = {
            'Single':      b'\x52\x0B\x03\x05\x00\x00\x53\x5E',
            'Continuous':  b'\x52\x0B\x03\x05\x01\x00\x53\x5F',
            'Normal':      b'\x52\x0B\x03\x07\x00\x00\x53\x5C',
            '3M/5M Image': b'\x52\x0B\x03\x07\x01\x00\x53\x5D',
        }

        ImageCaptureCmdString = ValueStateValues[value]
        self.__SetHelper('ImageCapture', ImageCaptureCmdString, value, qualifier)
    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x49\x01\x00\x53\x13',
            'Off': b'\x52\x0B\x03\x49\x00\x00\x53\x12',
        }

        LampCmdString = ValueStateValues[value]
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off',
        }

        LampCmdString = b'\x52\x0A\x01\x05\x53\x5D'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp: Invalid/unexpected response'])

    def SetLightBox(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x4A\x01\x00\x53\x10',
            'Off': b'\x52\x0B\x03\x4A\x00\x00\x53\x11',
        }

        LightBoxCmdString = ValueStateValues[value]
        self.__SetHelper('LightBox', LightBoxCmdString, value, qualifier)
    def UpdateLightBox(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off',
        }

        LightBoxCmdString = b'\x52\x0A\x01\x0C\x53\x54'
        res = self.__UpdateHelper('LightBox', LightBoxCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('LightBox', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['LightBox: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu':  b'\x52\x0B\x03\x41\x00\x00\x53\x1A',
            'Up':    b'\x52\x0B\x03\x42\x01\x00\x53\x18',
            'Down':  b'\x52\x0B\x03\x42\x00\x00\x53\x19',
            'Left':  b'\x52\x0B\x03\x42\x02\x00\x53\x1B',
            'Right': b'\x52\x0B\x03\x42\x03\x00\x53\x1A',
            'Enter': b'\x52\x0B\x03\x43\x00\x00\x53\x18',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetMirror(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x0E\x01\x00\x53\x54',
            'Off': b'\x52\x0B\x03\x0E\x00\x00\x53\x55',
        }

        MirrorCmdString = ValueStateValues[value]
        self.__SetHelper('Mirror', MirrorCmdString, value, qualifier)
    def SetOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = self.OutputResolutionValues[value]
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x1F\x01\x00\x53\x45',
            'Off': b'\x52\x0B\x03\x1F\x00\x00\x53\x44',
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left':  b'\x52\x0B\x03\x20\x00\x00\x53\x7B',
            'Top Left':     b'\x52\x0B\x03\x20\x01\x00\x53\x7A',
            'Top Right':    b'\x52\x0B\x03\x20\x02\x00\x53\x79',
            'Bottom Right': b'\x52\x0B\x03\x20\x03\x00\x53\x78',
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x01\x01\x00\x53\x5B',
            'Off': b'\x52\x0B\x03\x01\x00\x00\x53\x5A',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off',
            0x0A: 'Off',        # See notes in the top for extra value
        }

        PowerCmdString = b'\x52\x0A\x01\x04\x53\x5C'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x52\x0B\x03\x33\x00\x00\x53\x68',
            '2': b'\x52\x0B\x03\x33\x01\x00\x53\x69',
            '3': b'\x52\x0B\x03\x33\x02\x00\x53\x6A',
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x52\x0B\x03\x32\x00\x00\x53\x69',
            '2': b'\x52\x0B\x03\x32\x01\x00\x53\x68',
            '3': b'\x52\x0B\x03\x32\x02\x00\x53\x6B',
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
    def SetPreviewMode(self, value, qualifier):

        ValueStateValues = {
            'Sharp':      b'\x52\x0B\x03\x0A\x00\x00\x53\x51',
            'Graphic':    b'\x52\x0B\x03\x0A\x01\x00\x53\x50',
            'Motion':     b'\x52\x0B\x03\x0A\x02\x00\x53\x53',
            'Microscope': b'\x52\x0B\x03\x0A\x03\x00\x53\x52',
            'Macro':      b'\x52\x0B\x03\x0A\x04\x00\x53\x55',
            'Infinite':   b'\x52\x0B\x03\x0A\x05\x00\x53\x54',
            'Capture':    b'\x52\x0B\x03\x0B\x00\x00\x53\x50',
        }

        PreviewModeCmdString = ValueStateValues[value]
        self.__SetHelper('PreviewMode', PreviewModeCmdString, value, qualifier)
    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x23\x01\x00\x53\x79',
            'Off': b'\x52\x0B\x03\x23\x00\x00\x53\x78',
        }

        RecordCmdString = ValueStateValues[value]
        self.__SetHelper('Record', RecordCmdString, value, qualifier)
    def SetRotate(self, value, qualifier):

        ValueStateValues = {
            '0':   b'\x52\x0B\x03\x0F\x00\x00\x53\x54',
            '90':  b'\x52\x0B\x03\x0F\x01\x00\x53\x55',
            '180': b'\x52\x0B\x03\x0F\x02\x00\x53\x56',
            '270': b'\x52\x0B\x03\x0F\x03\x00\x53\x57',
        }

        RotateCmdString = ValueStateValues[value]
        self.__SetHelper('Rotate', RotateCmdString, value, qualifier)
    def SetSpotLightControl(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x52\x0B\x03\x19\x01\x00\x53\x43',
            'Off': b'\x52\x0B\x03\x19\x00\x00\x53\x42',
        }

        SpotLightControlCmdString = ValueStateValues[value]
        self.__SetHelper('SpotLightControl', SpotLightControlCmdString, value, qualifier)
    def SetSpotlightShade(self, value, qualifier):

        ValueStateValues = {
            '0%':   b'\x52\x0B\x03\x1A\x00\x00\x53\x41',
            '50%':  b'\x52\x0B\x03\x1A\x01\x00\x53\x40',
            '100%': b'\x52\x0B\x03\x1A\x02\x00\x53\x43',
        }

        SpotlightShadeCmdString = ValueStateValues[value]
        self.__SetHelper('SpotlightShade', SpotlightShadeCmdString, value, qualifier)
    def SetStorage(self, value, qualifier):

        ValueStateValues = {
            'Embedded':    b'\x52\x0B\x03\x28\x00\x00\x53\x73',
            'SD':          b'\x52\x0B\x03\x28\x01\x00\x53\x72',
            'Flash Drive': b'\x52\x0B\x03\x28\x02\x00\x53\x71',
        }

        StorageCmdString = ValueStateValues[value]
        self.__SetHelper('Storage', StorageCmdString, value, qualifier)
    def UpdateVideoOutputStatus(self, value, qualifier): 

        ValueStateValues = {
            0x00: 'VGA',
            0x01: 'TV',
        }

        VideoOutputStatusCmdString = b'\x52\x0A\x01\x07\x53\x5F'
        res = self.__UpdateHelper('VideoOutputStatus', VideoOutputStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('VideoOutputStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Output Status: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Zoom In':  b'\x52\x0B\x03\x46\x01\x00\x53\x1C',
            'Zoom Out': b'\x52\x0B\x03\x46\x00\x00\x53\x1D',
            'Reset':    b'\x52\x0B\x03\x47\x00\x00\x53\x1C',
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorCodes = {
            b'\x01': 'ID error',
            b'\x02': 'Checksum error',
            b'\x03': 'Not command',
            b'\x04': 'Function fail'
        }

        if response:
            if response[3:4] in ErrorCodes:
                self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, ErrorCodes[response[3:4]])])
                return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=7)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
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

    def aver_16_378_PL50(self):

        self.DisplayModeValues = {
            'Camera':   b'\x52\x0B\x03\x02\x00\x00\x53\x59',
            'Playback': b'\x52\x0B\x03\x03\x00\x00\x53\x58',
            'PC1':      b'\x52\x0B\x03\x04\x00\x00\x53\x5F',
            'PC2':      b'\x52\x0B\x03\x04\x01\x00\x53\x5E',
        }

        self.DisplayModeSates = {
            0x00: 'Camera',
            0x01: 'Playback',
            0x02: 'PC1',
            0x03: 'PC2',
        }

        self.OutputResolutionValues = {
            '1024x768':  b'\x52\x0B\x03\x2F\x01\x00\x53\x75',
            '1280x720':  b'\x52\x0B\x03\x2F\x02\x00\x53\x76',
            '1920x1080': b'\x52\x0B\x03\x2F\x03\x00\x53\x77',
            '1280x1024': b'\x52\x0B\x03\x2F\x04\x00\x53\x70',
            '1600x1200': b'\x52\x0B\x03\x2F\x05\x00\x53\x71',
            '1280x800':  b'\x52\x0B\x03\x2F\x06\x00\x53\x72',
        }

    def aver_16_378_M70(self):

        self.DisplayModeValues = {
            'Camera':   b'\x52\x0B\x03\x02\x00\x00\x53\x59',
            'Playback': b'\x52\x0B\x03\x03\x00\x00\x53\x58',
            'PC1':      b'\x52\x0B\x03\x04\x00\x00\x53\x5F',
        }

        self.DisplayModeSates = {
            0x00: 'Camera',
            0x01: 'Playback',
            0x02: 'PC1',
        }

        self.OutputResolutionValues = {
            '1024x768':  b'\x52\x0B\x03\x2F\x01\x00\x53\x75',
            '1280x720':  b'\x52\x0B\x03\x2F\x02\x00\x53\x76',
            '1920x1080': b'\x52\x0B\x03\x2F\x03\x00\x53\x77',
            '1280x1024': b'\x52\x0B\x03\x2F\x04\x00\x53\x70',
            '1600x1200': b'\x52\x0B\x03\x2F\x05\x00\x53\x71',
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

