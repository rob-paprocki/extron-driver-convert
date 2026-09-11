from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
            'Brightness': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'ImageRotation': {'Status': {}},
            'Input': {'Status': {}},
            'Lamp': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MicrophoneVolume': {'Status': {}},
            'OutputVolume': {'Status': {}},
            'PanMode': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xA0\x89([\x00-\xFF])\x00[\x00-\xFF]\xAF'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'\xA0\x78(\x01|\x00)\x00[\x00-\xFF]\xAF'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\xA0\x50(\x00|\x01|\x02)\x00[\x00-\xFF]\xAF'), self.__MatchLamp, None)
            self.AddMatchString(re.compile(b'\xA0\xD4([\x00-\xFF])[\x00-\xFF][\x00-\xFF]\xAF'), self.__MatchMicrophoneVolume, None)
            self.AddMatchString(re.compile(b'\xA0\xD7([\x00-\xFF])[\x00-\xFF][\x00-\xFF]\xAF'), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'\xA0\xB7(\x00|\x01)(\x00|\x01)[\x00-\xFF]\xAF'), self.__MatchPower, None)

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 105
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = pack('>BBBBBB', 0xA0, 0x30, 0x01, value, 0x00, 0xAF)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = b'\xA0\x89\x00\x00\x00\xAF'
        self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

    def __MatchBrightness(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Brightness', value, None)

    def UpdateDeviceStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusSpeedConstraints = {
            'Min': 0,
            'Max': 6
        }

        FocusState = {
            'Far': 0x01,
            'Near': 0x00,
            'Stop': b'\xA0\x19\x00\x00\x00\xAF'
        }

        FocusSpeed = int(qualifier['Focus Speed'])

        if FocusSpeedConstraints['Min'] <= FocusSpeed <= FocusSpeedConstraints['Max']:
            if value == 'Stop':
                FocusCmdString = FocusState['Stop']
            else:
                FocusCmdString = pack('>BBBBBB', 0xA0, 0x1A, FocusState[value], FocusSpeed, 0x00, 0xAF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': b'\xA0\x2C\x01\x00\x00\xAF',
            'Off': b'\xA0\x2C\x00\x00\x00\xAF'
        }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = FreezeState[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetImageRotation(self, value, qualifier):

        ImageRotationState = {
            '0': b'\xA0\xB4\x00\x00\x00\xAF',
            '180': b'\xA0\xB4\x01\x00\x00\xAF',
            'Flip': b'\xA0\xB4\x02\x00\x00\xAF',
            'Mirror': b'\xA0\xB4\x03\x00\x00\xAF'
        }

        ImageRotationCmdString = ImageRotationState[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA 1': b'\xA0\x3A\x00\x01\x00\xAF',
            'VGA 2': b'\xA0\x3A\x00\x00\x00\xAF',
            'Camera': b'\xA0\x3A\x01\x00\x00\xAF',
            'PC': b'\xA0\x3A\x02\x02\x00\xAF'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLamp(self, value, qualifier):

        LampState = {
            'Lamp On': b'\xA0\xC1\x01\x00\x00\xAF',
            'Backlight On': b'\xA0\xC1\x02\x00\x00\xAF',
            'Lamp + Backlight Off': b'\xA0\xC1\x00\x00\x00\xAF'
        }

        LampCmdString = LampState[value]
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        LampCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)

    def __MatchLamp(self, match, tag):

        LampState = {
            '\x01': 'Lamp On',
            '\x02': 'Backlight On',
            '\x00': 'Lamp + Backlight Off'
        }

        value = LampState[match.group(1).decode()]
        self.WriteStatus('Lamp', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\xA0\xA0\x02\x00\x00\xAF',
            'Down': b'\xA0\xA0\x03\x00\x00\xAF',
            'Left': b'\xA0\xA0\x04\x00\x00\xAF',
            'Right': b'\xA0\xA0\x05\x00\x00\xAF',
            'Enter': b'\xA0\xA0\x01\x00\x00\xAF',
            'Menu': b'\xA0\xA0\x06\x00\x00\xAF'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMicrophoneVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 16
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicrophoneVolumeCmdString = pack('>BBBBBB', 0xA0, 0xD4, value, 0x00, 0x00, 0xAF)
            self.__SetHelper('MicrophoneVolume', MicrophoneVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneVolume')

    def UpdateMicrophoneVolume(self, value, qualifier):

        MicrophoneVolumeCmdString = b'\xA0\xD5\x00\x00\x00\xAF'
        self.__UpdateHelper('MicrophoneVolume', MicrophoneVolumeCmdString, value, qualifier)

    def __MatchMicrophoneVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('MicrophoneVolume', value, None)

    def SetOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputVolumeCmdString = pack('>BBBBBB', 0xA0, 0xD6, value, 0x00, 0x00, 0xAF)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputVolumeCmdString = b'\xA0\xD7\x00\x00\x00\xAF'
        self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('OutputVolume', value, None)

    def SetPanMode(self, value, qualifier):

        PanModeState = {
            'On': b'\xA0\x26\x01\x00\x00\xAF',
            'Off': b'\xA0\x26\x00\x00\x00\xAF'
        }

        PanModeCmdString = PanModeState[value]
        self.__SetHelper('PanMode', PanModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\xA0\xB1\x01\x00\x00\xAF',
            'Off': b'\xA0\xB1\x00\x00\x00\xAF'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xA0\xB7\x00\x00\x00\xAF'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        DeviceStatusState = {
            '\x01': 'Ready to receive the command',
            '\x00': 'Standby to receive the command'
        }

        value = PowerState[match.group(2).decode()]
        self.WriteStatus('Power', value, None)

        value = DeviceStatusState[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetPreset(self, value, qualifier):

        PresetState = {
            'Load': b'\xA0\x03\x00\x00\x00\xAF',
            'Save': b'\xA0\x03\x00\x01\x00\xAF',
            'Reset': b'\xA0\x03\x01\x00\x00\xAF'
        }

        PresetCmdString = PresetState[value]
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        WhiteBalanceState = {
            'Auto Tune': b'\xA0\x22\x00\x00\x00\xAF',
            'AWB': b'\xA0\x22\x01\x00\x00\xAF'
        }

        WhiteBalanceCmdString = WhiteBalanceState[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomState = {
            'Tele': b'\xA0\x11\x00\x00\x00\xAF',
            'Wide': b'\xA0\x11\x01\x00\x00\xAF',
            'Stop': b'\xA0\x10\x00\x00\x00\xAF'
        }

        ZoomCmdString = ZoomState[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

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
