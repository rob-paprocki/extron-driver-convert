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
            'AspectRatio': {'Parameters': ['Zone'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoPower': {'Status': {}},
            'Input': {'Parameters': ['Zone'], 'Status': {}},
            'IRRemoteLock': {'Status': {}},
            'Keypad': {'Status': {}},
            'KeypadLock': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'PowerSavingMode': {'Status': {}},
            'Reboot': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT(?:\((ZONE\.[1-4])\))?:(AUTO|16X9|4X3|FILL|NATIVE|LETTERBOX)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'AUDIO\.MUTE:(ON|OFF)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'AUTO\.ON:(ON|OFF)\r'), self.__MatchAutoPower, None)
            self.AddMatchString(re.compile(b'SOURCE\.SELECT(?:\((ZONE\.[1-4]|ALL)\))?:(OPS|HDMI\.[1-4]|DP)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'IR\.LOCK:(ENABLE|DISABLE)\r'), self.__MatchIRRemoteLock, None)
            self.AddMatchString(re.compile(b'KEY\.LOCK:(ENABLE|DISABLE)\r'), self.__MatchKeypadLock, None)
            self.AddMatchString(re.compile(b'SYSTEM\.STATE:(POWERING\.ON|POWERING\.DOWN|ON|BACKLIGHT\.OFF|STANDBY|FAULT)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'POWER\.SAVE\.MODE:(DISABLED|LOW\.POWER|WAKE\.ON\.SIGNAL)\r'), self.__MatchPowerSavingMode, None)
            self.AddMatchString(re.compile(b'AUDIO\.VOLUME:(\d{1,2}|100)\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR \d\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ZoneStates = {
            '0': 'ZONE.1',
            '1': 'ZONE.2',
            '2': 'ZONE.3',
            '3': 'ZONE.4',
            '253': 'ALL.INPUT',
            '254': 'ALL',
            '255': 'ALL.ZONE',
            'Current': ''
        }

        AspectRatioState = {
            'Auto': 'AUTO',
            '16:9': '16X9',
            '4:3': '4X3',
            'Fill': 'FILL',
            'Native': 'NATIVE',
            'Letterbox': 'LETTERBOX'
        }

        if ZoneStates[qualifier['Zone']] == '':
            AspectRatioCmdString = 'ASPECT={0}\r'.format(AspectRatioState[value])
        else:
            AspectRatioCmdString = 'ASPECT({1})={0}\r'.format(AspectRatioState[value], ZoneStates[qualifier['Zone']])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ZoneStates = {
            '0': 'ZONE.1',
            '1': 'ZONE.2',
            '2': 'ZONE.3',
            '3': 'ZONE.4',
            '253': 'ALL.INPUT',
            '254': 'ALL',
            '255': 'ALL.ZONE',
            'Current': ''
        }

        if ZoneStates[qualifier['Zone']] == '':
            AspectRatioCmdString = 'ASPECT?\r'
        else:
            AspectRatioCmdString = 'ASPECT({0})?\r'.format(ZoneStates[qualifier['Zone']])
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ZoneStates = {
            'ZONE.1': '0',
            'ZONE.2': '1',
            'ZONE.3': '2',
            'ZONE.4': '3',
            'ALL.INPUT': '253',
            'ALL': '254',
            'ALL.ZONE': '255'
        }

        AspectRatioState = {
            'AUTO': 'Auto',
            '16X9': '16:9',
            '4X3': '4:3',
            'FILL': 'Fill',
            'NATIVE': 'Native',
            'LETTERBOX': 'Letterbox'
        }

        qualifier = {}
        if match.group(1):
            qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        else:
            qualifier['Zone'] = 'Current'
        value = AspectRatioState[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AudioMuteCmdString = 'AUDIO.MUTE={0}\r'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'AUDIO.MUTE?\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = AudioMuteState[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoPower(self, value, qualifier):

        AutoPowerState = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AutoPowerCmdString = 'AUTO.ON={0}\r'.format(AutoPowerState[value])
        self.__SetHelper('AutoPower', AutoPowerCmdString, value, qualifier)

    def UpdateAutoPower(self, value, qualifier):

        AutoPowerCmdString = 'AUTO.ON?\r'
        self.__UpdateHelper('AutoPower', AutoPowerCmdString, value, qualifier)

    def __MatchAutoPower(self, match, tag):

        AutoPowerState = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = AutoPowerState[match.group(1).decode()]
        self.WriteStatus('AutoPower', value, None)

    def SetInput(self, value, qualifier):

        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4',
            'All': 'ALL'
        }

        InputState = {
            'OPS': 'OPS',
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'HDMI 3': 'HDMI.3',
            'HDMI 4': 'HDMI.4',
            'DisplayPort': 'DP'
        }

        if ZoneStates[qualifier['Zone']] == '':
            InputCmdString = 'SOURCE.SELECT={0}\r'.format(InputState[value])
        else:
            InputCmdString = 'SOURCE.SELECT({1})={0}\r'.format(InputState[value], ZoneStates[qualifier['Zone']])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4',
            'All': 'ALL'
        }

        if ZoneStates[qualifier['Zone']] == '':
            InputCmdString = 'SOURCE.SELECT?\r'
        else:
            InputCmdString = 'SOURCE.SELECT({0})?\r'.format(ZoneStates[qualifier['Zone']])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ZoneStates = {
            'ZONE.1': '1',
            'ZONE.2': '2',
            'ZONE.3': '3',
            'ZONE.4': '4',
            'ALL': 'All'
        }

        InputState = {
            'OPS': 'OPS',
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'HDMI.3': 'HDMI 3',
            'HDMI.4': 'HDMI 4',
            'DP': 'DisplayPort'
        }

        qualifier = {}
        if match.group(1):
            qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        else:
            qualifier['Zone'] = 'Current'
        value = InputState[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetIRRemoteLock(self, value, qualifier):

        RemoteLockState = {
            'On': 'IR.LOCK=ENABLE\r',
            'Off': 'IR.LOCK=DISABLE\r'
        }

        IRRemoteLockCmdString = RemoteLockState[value]
        self.__SetHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)

    def UpdateIRRemoteLock(self, value, qualifier):

        IRRemoteLockCmdString = 'IR.LOCK?\r'
        self.__UpdateHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)

    def __MatchIRRemoteLock(self, match, tag):

        RemoteLockState = {
            'ENABLE': 'On',
            'DISABLE': 'Off'
        }

        value = RemoteLockState[match.group(1).decode()]
        self.WriteStatus('IRRemoteLock', value, None)

    def SetKeypad(self, value, qualifier):

        KeypadState = {
            '0': 'KEY=KEY.0\r',
            '1': 'KEY=KEY.1\r',
            '2': 'KEY=KEY.2\r',
            '3': 'KEY=KEY.3\r',
            '4': 'KEY=KEY.4\r',
            '5': 'KEY=KEY.5\r',
            '6': 'KEY=KEY.6\r',
            '7': 'KEY=KEY.7\r',
            '8': 'KEY=KEY.8\r',
            '9': 'KEY=KEY.9\r'
        }

        KeypadCmdString = KeypadState[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetKeypadLock(self, value, qualifier):

        KeypadLockState = {
            'On': 'KEY.LOCK=ENABLE\r',
            'Off': 'KEY.LOCK=DISABLE\r'
        }

        KeypadLockCmdString = KeypadLockState[value]
        self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def UpdateKeypadLock(self, value, qualifier):

        KeypadLockCmdString = 'KEY.LOCK?\r'
        self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def __MatchKeypadLock(self, match, tag):

        KeypadLockState = {
            'ENABLE': 'On',
            'DISABLE': 'Off'
        }

        value = KeypadLockState[match.group(1).decode()]
        self.WriteStatus('KeypadLock', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'UP',
            'Down': 'DOWN',
            'Left': 'LEFT',
            'Right': 'RIGHT',
            'Enter': 'ENTER',
            'Menu': 'MENU',
            'Previous Menu': 'MENU.PREV',
            'Exit': 'EXIT',
        }

        MenuNavigationCmdString = 'KEY={0}\r'.format(MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'DISPLAY.POWER=ON\r',
            'Off': 'DISPLAY.POWER=OFF\r',
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'SYSTEM.STATE?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            'ON': 'On',
            'STANDBY': 'Off',
            'POWERING.ON': 'Powering Up',
            'POWERING.DOWN': 'Powering Down',
            'BACKLIGHT.OFF': 'Backlight Off',
            'FAULT': 'Fault'
        }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPowerSavingMode(self, value, qualifier):

        PowerSavingModeState = {
            'On': 'LOW.POWER',
            'Off': 'DISABLED',
            'Wake On Signal': 'WAKE.ON.SIGNAL'
        }

        PowerSavingModeCmdString = 'POWER.SAVE.MODE={0}\r'.format(PowerSavingModeState[value])
        self.__SetHelper('PowerSavingMode', PowerSavingModeCmdString, value, qualifier)

    def UpdatePowerSavingMode(self, value, qualifier):

        PowerSavingModeCmdString = 'POWER.SAVE.MODE?\r'
        self.__UpdateHelper('PowerSavingMode', PowerSavingModeCmdString, value, qualifier)

    def __MatchPowerSavingMode(self, match, tag):

        PowerSavingModeState = {
            'LOW.POWER': 'On',
            'DISABLED': 'Off',
            'WAKE.ON.SIGNAL': 'Wake On Signal'
        }

        value = PowerSavingModeState[match.group(1).decode()]
        self.WriteStatus('PowerSavingMode', value, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'SYSTEM.REBOOT\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'AUDIO.VOLUME={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'AUDIO.VOLUME?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
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

        ERR_List = {
            '1': 'Invalid syntax',
            '2': 'Error Occured',
            '3': 'Command not recognized',
            '4': 'Invalid modifier',
            '5': 'Invalid operands',
            '6': 'Invalid operator'
        }
        match_value = ERR_List[match.group(1).decode()]
        value = 'ERR {0}: {1}'.format(match.group(1).decode(), match_value)
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
    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
