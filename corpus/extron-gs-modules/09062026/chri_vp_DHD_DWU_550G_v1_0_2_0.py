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
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
        }        

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Auto': '0',
            'Native': '1',
            '4:3': '2',
            'Letterbox': '3',
            'Full Size': '4',
            'Full Width': '5',
            'Full Height': '6',
        }

        AspectRatioCmdString = '(SZP{0})'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '0': 'Auto',
            '1': 'Native',
            '2': '4:3',
            '3': 'Letterbox',
            '4': 'Full Size',
            '5': 'Full Width',
            '6': 'Full Height',
        }

        AspectRatioCmdString = '(SZP?)'
        response = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

        if response:
            try:
                value = AspectRatioState[response[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(AIM1)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'Off': '(CLC0)',
            'CC1': '(CLC1)',
            'CC2': '(CLC2)',
        }

        ClosedCaptionCmdString = '{0}'.format(ClosedCaptionState[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            '0': 'Off',
            '1': 'CC1',
            '2': 'CC2',
        }

        ClosedCaptionCmdString = '(CLC?)'
        response = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

        if response:
            try:
                value = ClosedCaptionState[response[-2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaption')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '(FRZ{0})'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '(FRZ?)'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': '(SIN1)',
            'HDMI': '(SIN4)',
            'DVI': '(SIN5)',
            'Display Port': '(SIN6)',
            'Component': '(SIN7)',
            'S-Video': '(SIN8)',
            'Composite': '(SIN9)',
            'Christie Presenter': '(SIN10)',
            'Card Reader': '(SIN11)',
            'USB': '(SIN12)',
        }

        InputCmdString = '{0}'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            '!1': 'VGA',
            '!4': 'HDMI',
            '!5': 'DVI',
            '!6': 'Display Port',
            '!7': 'Component',
            '!8': 'S-Video',
            '!9': 'Composite',
            '10': 'Christie Presenter',
            '11': 'Card Reader',
            '12': 'USB',
        }

        InputNumberCmdString = '(SIN?)'
        response = self.__UpdateHelper('Input', InputNumberCmdString, value, qualifier)

        if response:
            try:
                value = InputState[response[-3:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '36',
            '1': '26',
            '2': '27',
            '3': '28',
            '4': '29',
            '5': '30',
            '6': '31',
            '7': '32',
            '8': '33',
            '9': '34'
        }

        KeypadCmdString = '(KEY{0})'.format(ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal': '(LPM0)',
            'Eco': '(LPM2)',
            'Auto': '(LPM1)',
        }

        LampModeCmdString = '{0}'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            '0': 'Normal',
            '2': 'Eco',
            '1': 'Auto',
        }

        LampModeCmdString = '(LPM?)'
        response = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

        if response:
            try:
                value = LampModeState[response[-2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '(LIF+LP1H?)'
        response = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

        if response:
            try:
                value = int(response[10:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '19',
            'Up': '38',
            'Right': '41',
            'Down': '42',
            'Left': '39',
            'Exit': '20',
            'Enter': '40'
        }

        MenuNavigationCmdString = '(KEY{0})'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayState = {
            'On': '(OSD1)',
            'Off': '(OSD0)',
        }

        OnScreenDisplayCmdString = '{0}'.format(OnScreenDisplayState[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayState = {
            '0': 'Off',
            '1': 'On',
        }

        OnScreenDisplayCmdString = '(OSD?)'
        response = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

        if response:
            try:
                value = OnScreenDisplayState[response[-2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'On': '(PIP1)',
            'Off': '(PIP0)',
        }

        PIPModeCmdString = '{0}'.format(PIPModeState[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeState = {
            '0': 'Off',
            '1': 'On',
        }

        PIPModeCmdString = '(PIP?)'
        response = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

        if response:
            try:
                value = PIPModeState[response[-2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPIPPosition(self, value, qualifier):

        PipPositionState = {
            'Left': '0',
            'Top': '1',
            'Right': '2',
            'Bottom': '3',
            'Bottom Right': '4',
            'Bottom Left': '5',
            'Top Left': '6',
            'Top Right': '7',
        }

        PipPositionCmdString = '(PPP{0})'.format(PipPositionState[value])
        self.__SetHelper('PIPPosition', PipPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PipPositionState = {
            '0': 'Left',
            '3': 'Bottom',
            '2': 'Right',
            '1': 'Top',
            '4': 'Bottom Right',
            '5': 'Bottom Left',
            '6': 'Top Left',
            '7': 'Top Right'
        }

        PipPositionCmdString = '(PPP?)'
        response = self.__UpdateHelper('PIPPosition', PipPositionCmdString, value, qualifier)

        if response:
            try:
                value = PipPositionState[response[-2]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPPosition')

    def SetPIPSize(self, value, qualifier):

        PIPSizeState = {
            'Small': '0',
            'Medium': '1',
            'Large': '2',
        }

        PIPSizeCmdString = '(PHS{0})'.format(PIPSizeState[value])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeState = {
            '0': 'Small',
            '1': 'Medium',
            '2': 'Large',
        }

        PIPSizeCmdString = '(PHS?)'
        response = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

        if response:
            try:
                value = PIPSizeState[response[-2]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPSize')

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '(PPS1)'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerControlState = {
            'On': '(PWR1)',
            'Off': '(PWR0)'
        }
        PowerControlCmdString = '{0}'.format(PowerControlState[value])
        self.__SetHelper('Power', PowerControlCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStatusState = {
            '!1': 'On',
            ',0': 'Off',
            '10': 'Cooling Down',
            '11': 'Warming Up'
        }

        PowerStatusCmdString = '(PWR?)'
        response = self.__UpdateHelper('Power', PowerStatusCmdString, value, qualifier)

        if response:
            try:
                value = PowerStatusState[response[-3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': '(SHU1)',
            'Off': '(SHU0)',
        }

        VideoMuteCmdString = '{0}'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            '1': 'On',
            '0': 'Off',
        }

        VideoMuteCmdString = '(SHU?)'
        response = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

        if response:
            try:
                value = VideoMuteState[response[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error = re.search('\([a-zA-Z0-9 ]+(\"[a-zA-Z0-9: ]+\")\)', response)
        if error is not None:
            print('Error: {0}'.format(error.group(1)))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=')')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=')')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

            

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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
