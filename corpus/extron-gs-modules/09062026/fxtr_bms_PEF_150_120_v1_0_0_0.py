from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'Fade': {'Parameters': ['Address', 'Group', 'Time'], 'Status': {}},
            'FadeStatus': {'Parameters': ['Address', 'Group'], 'Status': {}},
            'Flash': {'Parameters': ['Address', 'Group', 'Cycle Period'], 'Status': {}},
            'Level': {'Parameters': ['Address', 'Group', 'Rate', 'Time'], 'Status': {}},
            'LevelAbsolute': {'Parameters': ['Address', 'Group'], 'Status': {}},
            'LevelStatus': {'Parameters': ['Address', 'Group'], 'Status': {}},
            'NextFadeLevel': {'Parameters': ['Address', 'Group'], 'Status': {}},
            'StopFading': {'Parameters': ['Address', 'Group'], 'Status': {}},
            'StopFlashing': {'Parameters': ['Address', 'Group'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x01!f([0-9])([0-9]{1,2})\x02([\x00-\xFF]{18})\x17\x03'), self.__MatchAll, None)

    def __MatchAll(self, match, tag):

        Group = match.group(1).decode()
        Address = match.group(2).decode()
        Status = match.group(3).decode()
        Flashing = bool(ord(Status[2]) & 4)
        Fade = float(round(int(Status[13:16]) / 10, 1))

        self.WriteStatus('FadeStatus', Fade, {'Group': Group, 'Address': Address})

        if Flashing:
            Flash = int(Status[3]) * 10
            CyclePeriod = int(Status[4:6]) / 10
            self.WriteStatus('Flash', Flash, {'Group': Group, 'Address': Address, 'Cycle Period': CyclePeriod})
        else:
            Level = int(Status[3:6]) / 10
            self.WriteStatus('LevelStatus', Level, {'Group': Group, 'Address': Address})

    def SetFade(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 32
        }
        GroupConstraints = {
            'Min': 0,
            'Max': 9
        }
        TimeConstraints = {
            'Min': 0,
            'Max': 99.9
        }
        ValueStateValues = {
            'Up': 2,
            'Down': 1
        }

        try:
            Address = int(qualifier['Address'])
            Group = int(qualifier['Group'])
            Time = qualifier['Time']
            Mode = ValueStateValues[value]
        except:
            self.Discard('Invalid Command for SetFade')
        else:
            if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
                if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
                    if TimeConstraints['Min'] <= Time <= TimeConstraints['Max']:
                        FadeCmdString = '\x01f{0:03}\x02{1}{2}{3}\x17\x03'.format(int(Time * 10), Group, '/' * (Address - 1), Mode)
                        self.__SetHelper('Fade', FadeCmdString, value, qualifier)
                    else:
                        self.Discard('Invalid Command for SetFade')
                else:
                    self.Discard('Invalid Command for SetFade')
            else:
                self.Discard('Invalid Command for SetFade')

    def UpdateFadeStatus(self, value, qualifier):

        FadeStatusCmdString = '\x01?f{0}{1}\x02000018\x17\x03'.format(qualifier['Group'], qualifier['Address'])
        self.__UpdateHelper('FadeStatus', FadeStatusCmdString, value, qualifier)

    def SetFlash(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 32
        }
        GroupConstraints = {
            'Min': 0,
            'Max': 9
        }
        CyclePeriodConstraints = {
            'Min': 0.1,
            'Max': 9.9
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 90
        }

        try:
            Address = int(qualifier['Address'])
            Group = int(qualifier['Group'])
            CyclePeriod = qualifier['Cycle Period']
        except:
            self.Discard('Invalid Command for SetFlash')
        else:
            if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
                if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
                    if CyclePeriodConstraints['Min'] <= CyclePeriod <= CyclePeriodConstraints['Max']:
                        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                            FlashCmdString = '\x01f{0}{1:02}\x02{2}{3}4\x17\x03'.format(value // 10, int(CyclePeriod * 10), Group, '/' * (Address - 1))
                            self.__SetHelper('Flash', FlashCmdString, value, qualifier)
                    else:
                        self.Discard('Invalid Command for SetFlash')
                else:
                    self.Discard('Invalid Command for SetFlash')
            else:
                self.Discard('Invalid Command for SetFlash')

    def UpdateFlash(self, value, qualifier):

        FlashCmdString = '\x01?f{0}{1}\x02000018\x17\x03'.format(qualifier['Group'], qualifier['Address'])
        self.__UpdateHelper('Flash', FlashCmdString, value, qualifier)

    def UpdateHeartbeat(self, value, qualifier):

        HeartBeatCmdString = '\x01?f01\x02000018\x17\x03'
        self.__UpdateHelper('Heartbeat', HeartBeatCmdString, value, qualifier)

    def SetLevelAbsolute(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 32
        }
        GroupConstraints = {
            'Min': 0,
            'Max': 9
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 99.9
        }

        try:
            Address = int(qualifier['Address'])
            Group = int(qualifier['Group'])
        except:
            self.Discard('Invalid Command for SetLevelAbsolute')
        else:
            if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
                if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
                    if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                        LevelAbsoluteCmdString = '\x01f{0:03}\x02{1}{2}3\x17\x03'.format(int(value * 10), Group, '/' * (Address - 1))
                        self.__SetHelper('LevelAbsolute', LevelAbsoluteCmdString, value, qualifier)
                    else:
                        self.Discard('Invalid Command for SetLevelAbsolute')
                else:
                    self.Discard('Invalid Command for SetLevelAbsolute')
            else:
                self.Discard('Invalid Command for SetLevelAbsolute')

    def SetLevel(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 32
        }
        GroupConstraints = {
            'Min': 0,
            'Max': 9
        }
        RateConstraints = {
            'Min': 0,
            'Max': 99.9
        }
        TimeConstraints = {
            'Min': 0,
            'Max': 99.9
        }
        ValueStateValues = {
            'Up': ')',
            'Down': '('
        }

        try:
            Address = int(qualifier['Address'])
            Group = int(qualifier['Group'])
            Rate = qualifier['Rate']
            Time = qualifier['Time']
            Mode = ValueStateValues[value]
        except:
            self.Discard('Invalid Command for SetLevel')
        else:
            if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
                if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
                    if RateConstraints['Min'] <= Rate <= RateConstraints['Max']:
                        if TimeConstraints['Min'] <= Time <= TimeConstraints['Max']:
                            LevelCmdString = '\x01f{0:03}{1:03}\x02{2}{3}{4}\x17\x03'.format(int(Time * 10), int(Rate * 10), Group, '/' * (Address - 1), Mode)
                            self.__SetHelper('Level', LevelCmdString, value, qualifier)
                        else:
                            self.Discard('Invalid Command for SetLevel')
                    else:
                        self.Discard('Invalid Command for SetLevel')
                else:
                    self.Discard('Invalid Command for SetLevel')
            else:
                self.Discard('Invalid Command for SetLevel')

    def UpdateLevelStatus(self, value, qualifier):

        LevelStatusCmdString = '\x01?f{0}{1}\x02000018\x17\x03'.format(qualifier['Group'], qualifier['Address'])
        self.__UpdateHelper('LevelStatus', LevelStatusCmdString, value, qualifier)

    def SetNextFadeLevel(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 32
        }
        GroupConstraints = {
            'Min': 0,
            'Max': 9
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 99.9
        }

        try:
            Address = int(qualifier['Address'])
            Group = int(qualifier['Group'])
        except:
            self.Discard('Invalid Command for SetNextFadeLevel')
        else:
            if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
                if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
                    if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                        NextFadeLevelCmdString = '\x01f{0:03}\x02{1}{2}8\x17\x03'.format(int(value * 10), Group, '/' * (Address - 1))
                        self.__SetHelper('NextFadeLevel', NextFadeLevelCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetNextFadeLevel')
            else:
                self.Discard('Invalid Command for SetNextFadeLevel')

    def SetStopFading(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 32
        }
        GroupConstraints = {
            'Min': 0,
            'Max': 9
        }

        try:
            Address = int(qualifier['Address'])
            Group = int(qualifier['Group'])
        except:
            self.Discard('Invalid Command for SetStopFading')
        else:
            if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
                if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
                    StopFadingCmdString = '\x01f000\x02{0}{1}9\x17\x03'.format(Group, '/' * (Address - 1))
                    self.__SetHelper('StopFading', StopFadingCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetStopFading')
            else:
                self.Discard('Invalid Command for SetStopFading')

    def SetStopFlashing(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 32
        }
        GroupConstraints = {
            'Min': 0,
            'Max': 9
        }

        try:
            Address = int(qualifier['Address'])
            Group = int(qualifier['Group'])
        except:
            self.Discard('Invalid Command for SetStopFlashing')
        else:
            if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
                if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
                    StopFlashingCmdString = '\x01f000\x02{0}{1}5\x17\x03'.format(Group, '/' * (Address - 1))
                    self.__SetHelper('StopFlashing', StopFlashingCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetStopFlashing')
            else:
                self.Discard('Invalid Command for SetStopFlashing')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
