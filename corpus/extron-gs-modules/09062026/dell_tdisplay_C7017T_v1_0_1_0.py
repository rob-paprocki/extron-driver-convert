from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Brightness': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'Contrast': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Sharpness': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x6F\x6E\x83\x02\x00\x33(\x00|\x02|\x04)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02\x00\xB1(\x00|\x01)[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02\x00\x30([\x00-\x64])[\x00-\xFF]'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02\x00\x84(\x00|\x01)[\x00-\xFF]'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02\x00\x31([\x00-\x64])[\x00-\xFF]'), self.__MatchContrast, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x87\x02\x00\x62\x00\x00\x00(\x40|\x08|\x01|\x02|\x04)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02\x00\x00\x20(\x00|\x01|\x02)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02\x00\x34([\x00-\x64])[\x00-\xFF]'), self.__MatchSharpness, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02\x00\xB0([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x6F\x6E\x84\x02(\x01|\x02|\x03|\x04)[\x00-\xFF][\x00-\xFF][\x00-\xFF]'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '16:9': b'\x6E\x51\x83\xEA\x33\x00\x65',
            '4:3': b'\x6E\x51\x83\xEA\x33\x02\x67',
            '5:4': b'\x6E\x51\x83\xEA\x33\x04\x61'
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x6E\x51\x82\xEB\x33\x65'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '\x00': '16:9',
            '\x02': '4:3',
            '\x04': '5:4'
        }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': b'\x6E\x51\x83\xEA\xB1\x01\xE6',
            'Off': b'\x6E\x51\x83\xEA\xB1\x00\xE7'
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x6E\x51\x82\xEB\xB1\xE7'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = AudioMuteState[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            cks = (0x66 ^ value) & 0xFF
            BrightnessCmdString = pack('>BBBBBBB', 0x6E, 0x51, 0x83, 0xEA, 0x30, value, cks)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = b'\x6E\x51\x82\xEB\x30\x66'
        self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

    def __MatchBrightness(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Brightness', value, None)

    def SetButtonLock(self, value, qualifier):

        ButtonLockState = {
            'On': b'\x6E\x51\x83\xEA\x84\x01\xD3',
            'Off': b'\x6E\x51\x83\xEA\x84\x00\xD2'
        }

        ButtonLockCmdString = ButtonLockState[value]
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        ButtonLockCmdString = b'\x6E\x51\x82\xEB\x84\xD2'
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ButtonLockState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ButtonLockState[match.group(1).decode()]
        self.WriteStatus('ButtonLock', value, None)

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            cks = (0x67 ^ value) & 0xFF
            ContrastCmdString = pack('>BBBBBBB', 0x6E, 0x51, 0x83, 0xEA, 0x31, value, cks)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = b'\x6E\x51\x82\xEB\x34\x62'
        self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)

    def __MatchContrast(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Contrast', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': b'\x6E\x51\x86\xEA\x62\x00\x00\x00\x40\x71',
            'DisplayPort': b'\x6E\x51\x86\xEA\x62\x00\x00\x00\x08\x39',
            'HDMI 1': b'\x6E\x51\x86\xEA\x62\x00\x00\x00\x01\x30',
            'HDMI 2': b'\x6E\x51\x86\xEA\x62\x00\x00\x00\x02\x33',
            'HDMI 3': b'\x6E\x51\x86\xEA\x62\x00\x00\x00\x04\x35'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x6E\x51\x82\xEB\x62\x34'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '\x40': 'VGA',
            '\x08': 'DisplayPort',
            '\x01': 'HDMI 1',
            '\x02': 'HDMI 2',
            '\x04': 'HDMI 3'
        }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x6E\x51\x83\xEA\x20\x01\x77',
            'Off': b'\x6E\x51\x83\xEA\x20\x00\x76',
            'Standby': b'\x6E\x51\x83\xEA\x20\x02\x74'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x6E\x51\x82\xEB\x20\x76'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '\x01': 'On',
            '\x00': 'Off',
            '\x02': 'Standby'
        }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSharpness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            cks = (0x62 ^ value) & 0xFF
            SharpnessCmdString = pack('>BBBBBBB', 0x6E, 0x51, 0x83, 0xEA, 0x34, value, cks)
            self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')

    def UpdateSharpness(self, value, qualifier):

        SharpnessCmdString = b'\x6E\x51\x82\xEB\x34\x62'
        self.__UpdateHelper('Sharpness', SharpnessCmdString, value, qualifier)

    def __MatchSharpness(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Sharpness', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            cks = (0xE6 ^ value) & 0xFF
            VolumeCmdString = pack('>BBBBBBB', 0x6E, 0x51, 0x83, 0xEA, 0xB0, value, cks)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x6E\x51\x82\xEB\xB0\xE6'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Volume', value, None)

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

        DEVICE_ERROR_CODES = {
            '\x01': 'Timeout',
            '\x02': 'Parameter Error',
            '\x03': 'Not Connected',
            '\x04': 'Other Failure'
        }

        value = DEVICE_ERROR_CODES[match.group(1).decode()]
        self.Error([value])

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
