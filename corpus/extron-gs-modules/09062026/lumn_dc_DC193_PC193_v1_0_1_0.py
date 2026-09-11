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
            'AudioMicVolume': {'Status': {}},
            'AudioOutVolume': {'Status': {}},
            'AutoErase': {'Status': {}},
            'Brightness': {'Status': {}},
            'CaptureAction': {'Status': {}},
            'CaptureInterval': {'Status': {}},
            'CaptureTime': {'Status': {}},
            'Delete': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Function': {'Status': {}},
            'GammaMode': {'Status': {}},
            'ImageMode': {'Status': {}},
            'ImageQuality': {'Status': {}},
            'ImageRotation': {'Status': {}},
            'Lamp': {'Status': {}},
            'MaskMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MenuStatus': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PanMode': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'SlideShow': {'Status': {}},
            'SlideShowDelay': {'Status': {}},
            'SourceLive': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    def SetAudioMicVolume(self, value, qualifier):

        if 0 <= value <= 16:
            AudioMicVolumeCmdString = b''.join([b'\xA0\xD4', bytes([value]), b'\x00\x00\xAF'])
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
                self.Error(['AudioMicVolume: Invalid/unexpected response'])

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
            except (KeyError, IndexError):
                self.Error(['AudioOutVolume: Invalid/unexpected response'])

    def SetAutoErase(self, value, qualifier):

        state = bytes([{'On': 1, 'Off': 0}[value]])
        AutoEraseCmdString = b''.join([b'\xA0\x14', state, b'\x00\x00\xAF'])
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

        state = bytes([{'Single Capture': 0, 'Time Lapse': 1, 'Record': 2, 'Disabled': 3}[value]])
        CaptureActionCmdString = b''.join([b'\xA0\x96', state, b'\x00\x00\xAF'])
        self.__SetHelper('CaptureAction', CaptureActionCmdString, value, qualifier)

    def SetCaptureInterval(self, value, qualifier):

        state = bytes([{'3 sec': 0, '5 sec': 1, '10 sec': 2, '30 sec': 3, '1 min': 4, '2 min': 5, '5 min': 6}[value]])
        CaptureIntervalCmdString = b''.join([b'\xA0\x97', state, b'\x00\x00\xAF'])
        self.__SetHelper('CaptureInterval', CaptureIntervalCmdString, value, qualifier)

    def SetCaptureTime(self, value, qualifier):

        state = bytes([{'1 hr': 0, '2 hr': 1, '4 hr': 2, '8 hr': 3, '24 hr': 4, '48 hr': 5, '72 hr': 6}[value]])
        CaptureTimeCmdString = b''.join([b'\xA0\x98', state, b'\x00\x00\xAF'])
        self.__SetHelper('CaptureTime', CaptureTimeCmdString, value, qualifier)

    def SetDelete(self, value, qualifier):

        state = bytes([{'Delete One': 0, 'Delete All': 1, 'Format': 2}[value]])
        DeleteCmdString = b''.join([b'\xA0\xB6', state, b'\x00\x00\xAF'])
        self.__SetHelper('Delete', DeleteCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        speed = int(qualifier['Speed'])
        if 0 <= speed <= 6:
            state = bytes([{'Far': 1, 'Near': 0, 'Stop': 0}[value], 0 if value == 'Stop' else speed])
            focusState = b'\x19' if value == 'Stop' else b'\x1A'
            self.__SetHelper('Focus', b''.join([b'\xA0', focusState, state, b'\x00\xAF']), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        state = bytes([{'On': 1, 'Off': 0}[value]])
        FreezeCmdString = b''.join([b'\xA0\x2C', state, b'\x00\x00\xAF'])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = {1: 'On', 0: 'Off'}[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetFunction(self, value, qualifier):

        state = {'AF One Push Trigger': b'\xA3\x01', 'AWB Correction': b'\x56\x00', 'Capture': b'\xB2\x00', 'Copy to USB': b'\x08\x00', 'Factory Reset': b'\x03\x01', 'Playback Thumbnail': b'\xB3\x00',
                 'Record': b'\xB2\x01'}[value]
        FunctionCmdString = b''.join([b'\xA0', state, b'\x00\x00\xAF'])
        self.__SetHelper('Function', FunctionCmdString, value, qualifier)

    def SetGammaMode(self, value, qualifier):

        state = bytes([{'Photo': 0, 'Text': 1, 'Gray': 2}[value]])
        GammaModeCmdString = b''.join([b'\xA0\xA7', state, b'\x00\x00\xAF'])
        self.__SetHelper('GammaMode', GammaModeCmdString, value, qualifier)

    def UpdateGammaMode(self, value, qualifier):

        GammaModeCmdString = b'\xA0\x51\x00\x00\x00\xAF'
        res = self.__UpdateHelper('GammaMode', GammaModeCmdString, value, qualifier)
        if res:
            try:
                value = {0: 'Photo', 1: 'Text', 2: 'Gray'}[res[2]]
                self.WriteStatus('GammaMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['GammaMode: Invalid/unexpected response'])

    def SetImageMode(self, value, qualifier):

        state = bytes([{'Normal': 0, 'Slide': 1, 'Film': 2, 'Microscope': 3}[value]])
        ImageModeCmdString = b''.join([b'\xA0\xA9', state, b'\x00\x00\xAF'])
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)

    def SetImageQuality(self, value, qualifier):

        state = bytes([{'High': 0, 'Medium': 1, 'Low': 2}[value]])
        ImageQualityCmdString = b''.join([b'\xA0\x07', state, b'\x00\x00\xAF'])
        self.__SetHelper('ImageQuality', ImageQualityCmdString, value, qualifier)

    def SetImageRotation(self, value, qualifier):

        state = bytes([{'0': 0, '180': 1, 'Flip': 2, 'Mirror': 3}[value]])
        ImageRotationCmdString = b''.join([b'\xA0\xB4', state, b'\x00\x00\xAF'])
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def SetLamp(self, value, qualifier):

        state = bytes([{'Lamp and Head LED Off': 0, 'Lamp and Head LED On': 1, 'Lamp On': 2, 'Head LED On': 3}[value]])
        LampCmdString = b''.join([b'\xA0\xC1', state, b'\x00\x00\xAF'])
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        LampCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = {0: 'Lamp and Head LED Off', 1: 'Lamp and Head LED On', 2: 'Lamp On', 3: 'Head LED On'}[res[2]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp: Invalid/unexpected response'])

    def SetMaskMode(self, value, qualifier):

        state = bytes([{'Disable': 0, 'Mask': 1, 'Spotlight': 2}[value]])
        MaskModeCmdString = b''.join([b'\xA0\x27', state, b'\x00\x00\xAF'])
        self.__SetHelper('MaskMode', MaskModeCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        state = bytes([{'Up': 1, 'Down': 2, 'Left': 3, 'Right': 4, 'Menu': 5, 'Enter': 6, 'Page Up': 1, 'Page Down': 0}[value]])
        menuState = b'\x4A' if 'Page' in value else b'\xA0'
        self.__SetHelper('MenuNavigation', b''.join([b'\xA0', menuState, state, b'\x00\xAF']), value, qualifier)

    def UpdateMenuStatus(self, value, qualifier):

        MenuStatusCmdString = b'\xA0\x8B\x00\x00\x00\xAF'
        res = self.__UpdateHelper('MenuStatus', MenuStatusCmdString, value, qualifier)
        if res:
            try:
                value = {1: 'On', 0: 'Off'}[res[2]]
                self.WriteStatus('MenuStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['MenuStatus: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        state = bytes([{'On': 1, 'Off': 0}[value]])
        OnScreenDisplayCmdString = b''.join([b'\xA0\x4B', state, b'\x00\x00\xAF'])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPanMode(self, value, qualifier):

        state = bytes([{'On': 1, 'Off': 0}[value]])
        PanModeCmdString = b''.join([b'\xA0\x26', state, b'\x00\x00\xAF'])
        self.__SetHelper('PanMode', PanModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        state = bytes([{'On': 1, 'Off': 0}[value]])
        PowerCmdString = b''.join([b'\xA0\xB1', state, b'\x00\x00\xAF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xA0\xB7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if res[2] == 0:
                    value = 'Not Ready'
                else:
                    value = {1: 'On', 0: 'Off'}[res[3]]
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

        state = bytes([{'On': 1, 'Off': 0}[value]])
        SlideShowCmdString = b''.join([b'\xA0\x04', state, b'\x00\x00\xAF'])
        self.__SetHelper('SlideShow', SlideShowCmdString, value, qualifier)

    def SetSlideShowDelay(self, value, qualifier):

        state = bytes([{'0.5 sec': 0, '1.0 sec': 1, '3.0 sec': 2, '5.0 sec': 3, '10.0 sec': 4, 'Manual': 5}[value]])
        SlideShowDelayCmdString = b''.join([b'\xA0\x06', state, b'\x00\x00\xAF'])
        self.__SetHelper('SlideShowDelay', SlideShowDelayCmdString, value, qualifier)

    def SetSourceLive(self, value, qualifier):

        state = bytes([{'Camera': 0, 'PC': 1, 'Off': 2}[value], 0])
        SourceLiveCmdString = b'\x3A'
        self.__SetHelper('SourceLive', SourceLiveCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        state = bytes([{'Auto Tune': 0, 'AWB': 1}[value]])
        WhiteBalanceCmdString = b''.join([b'\xA0\x22', state, b'\x00\x00\xAF'])
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        state = {'Tele': b'\x11\x00', 'Wide': b'\x11\x01', 'Stop': b'\x10\x00'}[value]
        self.__SetHelper('Zoom', b''.join([b'\xA0', state, b'\x00\x00\xAF']), value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response[-2]
        error_states = {1: 'NAK (No Action)', 2: 'Ignore (Command is not in the command list)'}
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
                res = self.__CheckResponseForErrors(command)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
