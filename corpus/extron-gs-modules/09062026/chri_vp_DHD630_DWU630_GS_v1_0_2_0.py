from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LightSourceMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(SZP!([0123456])\)'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\(CLC!([012])\)'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\(FRZ!([01])\)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\(SIN\+MAIN!0?([123458])\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(LPM!([013])\)'), self.__MatchLightSourceMode, None)
            self.AddMatchString(re.compile(b'\(LIF\+TPHS!(\d+)\)'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\(SIN\+PIP!([123458])\)'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\(PIP!([01])\)'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\(PPP!([01234567])\)'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\(PHS!([012])\)'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\(PWR!([01])\)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(SHU!0?([01])\)'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\(\d+ \d+ (ERR\d+ \".+\")\)'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Auto': '(SZP 0)',
            'Native': '(SZP 1)',
            '4:3': '(SZP 2)',
            'LetterBox': '(SZP 3)',
            'Full Size': '(SZP 4)',
            'Full Width': '(SZP 5)',
            'Full Height': '(SZP 6)'
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '(SZP?)'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '0': 'Auto',
            '1': 'Native',
            '2': '4:3',
            '3': 'LetterBox',
            '4': 'Full Size',
            '5': 'Full Width',
            '6': 'Full Height'
        }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'CC1': '(CLC 1)',
            'CC2': '(CLC 2)',
            'Off': '(CLC 0)'
        }

        ClosedCaptionCmdString = ClosedCaptionState[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = '(CLC?)'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionState = {
            '1': 'CC1',
            '2': 'CC2',
            '0': 'Off'
        }

        value = ClosedCaptionState[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': '(FRZ 1)',
            'Off': '(FRZ 0)'
        }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '(FRZ?)'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeState = {
            '1': 'On',
            '0': 'Off'
        }

        value = FreezeState[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': '(SIN+MAIN 1)',
            'BNC': '(SIN+MAIN 2)',
            'HDMI 1': '(SIN+MAIN 3)',
            'HDMI 2': '(SIN+MAIN 4)',
            'DVI-D': '(SIN+MAIN 5)',
            'HDBaseT': '(SIN+MAIN 8)'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SIN+MAIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '1': 'VGA',
            '2': 'BNC',
            '3': 'HDMI 1',
            '4': 'HDMI 2',
            '5': 'DVI-D',
            '8': 'HDBaseT'
        }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        KeypadState = {
            '1': '(KEY 26)',
            '2': '(KEY 27)',
            '3': '(KEY 28)',
            '4': '(KEY 29)',
            '5': '(KEY 30)',
            '6': '(KEY 31)',
            '7': '(KEY 32)',
            '8': '(KEY 33)',
            '9': '(KEY 34)',
            '0': '(KEY 36)'
        }

        KeypadCmdString = KeypadState[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetLightSourceMode(self, value, qualifier):

        LightSourceModeState = {
            'Normal': '(LPM 0)',
            'High': '(LPM 1)',
            'Eco': '(LPM 3)'
        }

        LightSourceModeCmdString = LightSourceModeState[value]
        self.__SetHelper('LightSourceMode', LightSourceModeCmdString, value, qualifier)

    def UpdateLightSourceMode(self, value, qualifier):

        LightSourceModeCmdString = '(LPM?)'
        self.__UpdateHelper('LightSourceMode', LightSourceModeCmdString, value, qualifier)

    def __MatchLightSourceMode(self, match, tag):

        LightSourceModeState = {
            '0': 'Normal',
            '1': 'High',
            '3': 'Eco'
        }

        value = LightSourceModeState[match.group(1).decode()]
        self.WriteStatus('LightSourceMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': '(KEY 38)',
            'Down': '(KEY 42)',
            'Left': '(KEY 39)',
            'Right': '(KEY 41)',
            'Enter': '(KEY 40)',
            'Menu': '(KEY 19)',
            'Exit': '(KEY 20)'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '(LIF+TPHS?)'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
            'VGA': '(SIN+PIP 1)',
            'BNC': '(SIN+PIP 2)',
            'HDMI 1': '(SIN+PIP 3)',
            'HDMI 2': '(SIN+PIP 4)',
            'DVI-D': '(SIN+PIP 5)',
            'HDBaseT': '(SIN+PIP 8)'
        }

        PIPInputCmdString = PIPInputState[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '(SIN+PIP?)'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        PIPInputState = {
            '1': 'VGA',
            '2': 'BNC',
            '3': 'HDMI 1',
            '4': 'HDMI 2',
            '5': 'DVI-D',
            '8': 'HDBaseT'
        }

        value = PIPInputState[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'On': '(PIP 1)',
            'Off': '(PIP 0)'
        }

        PIPModeCmdString = PIPModeState[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '(PIP?)'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        PIPModeState = {
            '1': 'On',
            '0': 'Off'
        }

        value = PIPModeState[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
            'Left Vertical Center': '(PPP 0)',
            'Top Center': '(PPP 1)',
            'Right Vertical Center': '(PPP 2)',
            'Bottom Center': '(PPP 3)',
            'Bottom Right': '(PPP 4)',
            'Bottom Left': '(PPP 5)',
            'Top Left': '(PPP 6)',
            'Top Right': '(PPP 7)'
        }

        PIPPositionCmdString = PIPPositionState[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = '(PPP?)'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        PIPPositionState = {
            '0': 'Left Vertical Center',
            '1': 'Top Center',
            '2': 'Right Vertical Center',
            '3': 'Bottom Center',
            '4': 'Bottom Right',
            '5': 'Bottom Left',
            '6': 'Top Left',
            '7': 'Top Right'
        }

        value = PIPPositionState[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        PIPSizeState = {
            'Small': '(PHS 0)',
            'Medium': '(PHS 1)',
            'Large': '(PHS 2)'
        }

        PIPSizeCmdString = PIPSizeState[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = '(PHS?)'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        PIPSizeState = {
            '0': 'Small',
            '1': 'Medium',
            '2': 'Large'
        }

        value = PIPSizeState[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '(PPS)'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': '(PWR 1)',
            'Off': '(PWR 0)'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '(PWR?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '1': 'On',
            '0': 'Off'
        }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': '(SHU 1)',
            'Off': '(SHU 0)'
        }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '(SHU?)'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteState = {
            '1': 'On',
            '0': 'Off'
        }

        value = VideoMuteState[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.Error(['There was an error in the device response: ' + match.group(1).decode()])

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
