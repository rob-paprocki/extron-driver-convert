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
            'AutoFocus': {'Status': {}},
            'Color': {'Status': {}},
            'Display': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Gamma': {'Status': {}},
            'ImageRotation': {'Status': {}},
            'ImageSave': {'Status': {}},
            'Input': {'Status': {}},
            'Iris': {'Status': {}},
            'Light': {'Status': {}},
            'PosNeg': {'Status': {}},
            'SlideShow': {'Status': {}},
            'SlideShowRepeat': {'Status': {}},
            'TextEnhancer': {'Status': {}},
            'USBMode': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = '\x02AF0\x20\x20\x03'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetColor(self, value, qualifier):

        ColorState = {
            'Color': '0',
            'B/W': '1'
        }

        ColorCmdString = '\x02CB{0}\x20\x20\x03'.format(ColorState[value])
        self.__SetHelper('Color', ColorCmdString, value, qualifier)

    def UpdateColor(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetDisplay(self, value, qualifier):

        DisplayState = {
            'Single': '0',
            '3x3': '1',
            '4x4': '2'
        }

        DisplayCmdString = '\x02DP{0}\x20\x20\x03'.format(DisplayState[value])
        self.__SetHelper('Display', DisplayCmdString, value, qualifier)

    def UpdateDisplay(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Off': '0',
            'On': '1'
        }

        ExecutiveModeCmdString = '\x02LL{0}\x20\x20\x03'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusState = {
            'Near': '+',
            'Far': '-',
            'Stop': '0'
        }

        FocusCmdString = '\x02FO{0}\x20\x20\x03'.format(FocusState[value])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'Off': '0',
            'On': '1'
        }

        FreezeCmdString = '\x02FZ{0}\x20\x20\x03'.format(FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetGamma(self, value, qualifier):

        GammaState = {
            'Normal': '1',
            'High': '0',
            'Low': '2'
        }

        GammaCmdString = '\x02GM{0}\x20\x20\x03'.format(GammaState[value])
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        self.UpdateTextEnhancer(value, qualifier)

    def SetImageRotation(self, value, qualifier):

        ImageRotationState = {
            '0': '0',
            '180': '1'
        }

        ImageRotationCmdString = '\x02RO{0}\x20\x20\x03'.format(ImageRotationState[value])
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def UpdateImageRotation(self, value, qualifier):

        self.UpdateTextEnhancer(value, qualifier)

    def SetImageSave(self, value, qualifier):

        ImageSaveCmdString = '\x02CA0\x20\x20\x03'
        self.__SetHelper('ImageSave', ImageSaveCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'RGB': '1',
            'SD': '2',
            'Camera': '0'
        }

        InputCmdString = '\x02AV{0}\x20\x20\x03'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):  # Response:  \x02[Lamp]X[Pos/Neg][Color][Input][Display][Freeze]X\x03

        LightState = {
            '1': 'Base',
            '2': 'Upper',
            '0': 'Off'
        }

        PosNegState = {
            '0': 'Pos',
            '1': 'Neg'
        }

        ColorState = {
            '0': 'Color',
            '1': 'B/W'
        }

        InputState = {
            '0': 'Camera',
            '1': 'RGB',
            '2': 'SD'
        }

        DisplayState = {
            '0': 'Single',
            '1': '3x3',
            '2': '4x4'
        }

        FreezeState = {
            '0': 'Off',
            '1': 'On'
        }

        InputCmdString = '\x02QS0\x20\x20\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = LightState[res[1]]
                self.WriteStatus('Light', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Light : Invalid/Unexpected Response'])

            try:
                value = PosNegState[res[3]]
                self.WriteStatus('PosNeg', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PosNeg : Invalid/Unexpected Response'])

            try:
                value = ColorState[res[4]]
                self.WriteStatus('Color', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color : Invalid/Unexpected Response'])

            try:
                value = InputState[res[5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected Response'])

            try:
                value = DisplayState[res[6]]
                self.WriteStatus('Display', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display : Invalid/Unexpected Response'])

            try:
                value = FreezeState[res[7]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze : Invalid/Unexpected Response'])
        else:
            self.Discard('Device Is Busy for UpdateInput')

    def SetIris(self, value, qualifier):

        IrisState = {
            'Open': '+',
            'Close': '-',
            'Stop': '0',
            'Auto': '1',
            'Manual': '2'
        }

        IrisCmdString = '\x02IR{0}\x20\x20\x03'.format(IrisState[value])
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def UpdateIris(self, value, qualifier):

        self.UpdateTextEnhancer(value, qualifier)

    def SetLight(self, value, qualifier):

        LightState = {
            'Base': '1',
            'Upper': '2',
            'Off': '0'
        }

        LightCmdString = '\x02PL{0}\x20\x20\x03'.format(LightState[value])
        self.__SetHelper('Light', LightCmdString, value, qualifier)

    def UpdateLight(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetPosNeg(self, value, qualifier):

        PosNegState = {
            'Pos': '0',
            'Neg': '1'
        }

        PosNegCmdString = '\x02NP{0}\x20\x20\x03'.format(PosNegState[value])
        self.__SetHelper('PosNeg', PosNegCmdString, value, qualifier)

    def UpdatePosNeg(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetSlideShow(self, value, qualifier):

        SlideShowState = {
            'Start': '1',
            'Stop': '0'
        }

        SlideShowCmdString = '\x02SS{0}\x20\x20\x03'.format(SlideShowState[value])
        self.__SetHelper('SlideShow', SlideShowCmdString, value, qualifier)

    def SetSlideShowRepeat(self, value, qualifier):

        SlideShowRepeatState = {
            'On': '0',
            'Off': '1'
        }

        SlideShowRepeatCmdString = '\x02SR{0}\x20\x20\x03'.format(SlideShowRepeatState[value])
        self.__SetHelper('SlideShowRepeat', SlideShowRepeatCmdString, value, qualifier)

    def SetTextEnhancer(self, value, qualifier):

        TextEnhancerState = {
            'Graphics': '0',
            'Text1': '1',
            'Text2': '2',
            'Text3': '3'
        }

        TextEnhancerCmdString = '\x02CT{0}\x20\x20\x03'.format(TextEnhancerState[value])
        self.__SetHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier)

    def UpdateTextEnhancer(self, value, qualifier):  # Response:  \x02[Iris][Gamma][ImageRotation]XX[Text]X[USB]\x03

        IrisState = {
            '1': 'Auto',
            '2': 'Manual'
        }

        GammaState = {
            '0': 'High',
            '1': 'Normal',
            '2': 'Low'
        }

        ImageRotationState = {
            '0': '0',
            '1': '180'
        }

        TextEnhancerState = {
            '0': 'Graphics',
            '1': 'Text1',
            '2': 'Text2',
            '3': 'Text3'
        }

        USBModeState = {
            '0': 'Storage',
            '1': 'Application'
        }

        TextEnhancerCmdString = '\x02QS2\x20\x20\x03'
        res = self.__UpdateHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier)
        if res:
            try:
                value = IrisState[res[1]]
                self.WriteStatus('Iris', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Iris : Invalid/Unexpected Response'])

            try:
                value = GammaState[res[2]]
                self.WriteStatus('Gamma', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Gamma : Invalid/Unexpected Response'])

            try:
                value = ImageRotationState[res[3]]
                self.WriteStatus('ImageRotation', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Image Rotation : Invalid/Unexpected Response'])

            try:
                value = TextEnhancerState[res[6]]
                self.WriteStatus('TextEnhancer', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Text Enhancer : Invalid/Unexpected Response'])

            try:
                value = USBModeState[res[8]]
                self.WriteStatus('USBMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['USB Mode : Invalid/Unexpected Response'])
        else:
            self.Discard('Device Is Busy for UpdateTextEnhancer')

    def SetUSBMode(self, value, qualifier):

        USBModeState = {
            'Application': '1',
            'Storage': '0'
        }

        USBModeCmdString = '\x02UM{0}\x20\x20\x03'.format(USBModeState[value])
        self.__SetHelper('USBMode', USBModeCmdString, value, qualifier)

    def UpdateUSBMode(self, value, qualifier):

        self.UpdateTextEnhancer(value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomState = {
            'Tele': '+',
            'Wide': '-',
            'Stop': '0'
        }

        ZoomCmdString = '\x02ZO{0}\x20\x20\x03'.format(ZoomState[value])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'NAK' in response:
            self.Error(['{0}: Negative Acknowledgement'.format(sourceCmdName)])
            response = b''
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if res:
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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

