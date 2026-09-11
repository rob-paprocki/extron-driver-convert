import re
from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'MonitorButtonLock': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControlLock': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False' and self.ConnectionType == 'Ethernet':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioPCState = {
            'Wide': 'WIDE0001\r\n',
            'Normal': 'WIDE0002\r\n',
            'Dot by Dot': 'WIDE0003\r\n'
            }

        AspectRatioAVState = {
            'Wide': 'WIDE0001\r\n',
            'Normal': 'WIDE0004\r\n',
            'Dot by Dot': 'WIDE0005\r\n'
            }

        InputType = qualifier['Input']
        AspectRatioCmdString = None
        if InputType not in ['PC', 'AV']:
            print('Invalid Command for SetAspectRatio')
        else:
            if InputType == 'PC':
                AspectRatioCmdString = AspectRatioPCState[value]
            elif InputType == 'AV':
                AspectRatioCmdString = AspectRatioAVState[value]

        if AspectRatioCmdString:
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioPCState = {
            '1': 'Wide',
            '2': 'Normal',
            '3': 'Dot by Dot'
            }

        AspectRatioAVState = {
            '1': 'Wide',
            '4': 'Normal',
            '5': 'Dot by Dot'
            }

        InputType = qualifier['Input']

        AspectRatioCmdString = 'WIDE????\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if InputType == 'PC':
                    value = AspectRatioPCState[res[0:1]]
                elif InputType == 'AV':
                    value = AspectRatioAVState[res[0:1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ASNC0001\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'DVI-D': 'INPS0001\r\n',
            'D-SUB (RGB)': 'INPS0002\r\n',
            'D-SUB (Component)': 'INPS0003\r\n',
            'D-SUB (Video)': 'INPS0004\r\n',
            'HDMI (AV)': 'INPS0009\r\n',
            'HDMI (PC)': 'INPS0010\r\n',
            'Media Player': 'INPS0011\r\n'
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            1: 'DVI-D',
            2: 'D-SUB (RGB)',
            3: 'D-SUB (Component)',
            4: 'D-SUB (Video)',
            9: 'HDMI (AV)',
            10: 'HDMI (PC)',
            11: 'Media Player'
            }

        InputCmdString = 'INPS????\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except KeyError:
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetMonitorButtonLock(self, value, qualifier):

        MonitorButtonLockState = {
            'Unlocked': 'ALCM0000\r\n',
            'Lock All': 'ALCM0001\r\n',
            'Lock Except Power': 'ALCM0003\r\n'
            }

        MonitorButtonLockCmdString = MonitorButtonLockState[value]
        self.__SetHelper('MonitorButtonLock', MonitorButtonLockCmdString, value, qualifier)

    def UpdateMonitorButtonLock(self, value, qualifier):

        MonitorButtonLockState = {
            '0': 'Unlocked',
            '1': 'Lock All',
            '3': 'Lock Except Power'
            }

        MonitorButtonLockCmdString = 'ALCM????\r\n'
        res = self.__UpdateHelper('MonitorButtonLock', MonitorButtonLockCmdString, value, qualifier)
        if res:
            try:
                value = MonitorButtonLockState[res[0:1]]
                self.WriteStatus('MonitorButtonLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Monitor Button Lock: Invalid/Unexpected Response'])

    def SetMute(self, value, qualifier):

        MuteState = {
            'On': 'MUTE0001\r\n',
            'Off': 'MUTE0000\r\n'
            }

        MuteCmdString = MuteState[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteState = {
            '1': 'On',
            '0': 'Off'
            }

        MuteCmdString = 'MUTE????\r\n'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteState[res[0:1]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'POWR0001\r\n',
            'Off': 'POWR0000\r\n',
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input signal waiting mode'
            }

        PowerCmdString = 'POWR????\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[0:1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetRemoteControlLock(self, value, qualifier):

        RemoteControlLockState = {
            'Unlocked': 'ALCR0000\r\n',
            'Lock All': 'ALCR0001\r\n',
            'Lock Except Volume': 'ALCR0002\r\n',
            'Lock Except Power': 'ALCR0003\r\n'
            }

        RemoteControlLockCmdString = RemoteControlLockState[value]
        self.__SetHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)

    def UpdateRemoteControlLock(self, value, qualifier):

        RemoteControlLockState = {
            '0': 'Unlocked',
            '1': 'Lock All',
            '2': 'Lock Except Volume',
            '3': 'Lock Except Power'
            }

        RemoteControlLockCmdString = 'ALCR????\r\n'
        res = self.__UpdateHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)
        if res:
            try:
                value = RemoteControlLockState[res[0:1]]
                self.WriteStatus('RemoteControlLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Remote Control Lock: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM00{0:02d}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except ValueError:
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Login:' in response:
            self.DriverCmd('SetUsername', None, None)
        elif 'Password:' in response:
            self.DriverCmd('SetPassword', None, None)
        elif 'ERR' in response:
            self.Error(['{0}: Communication error or incorrect command'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

        # Add regular expression so that it can be check on incoming data from device.

    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


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