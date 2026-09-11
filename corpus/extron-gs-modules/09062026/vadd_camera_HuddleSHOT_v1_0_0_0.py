from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'AutoWhiteBalance': {'Status': {}},
            'BacklightCompensation': {'Status': {}},
            'Dewarp': {'Status': {}},
            'IndicatorLight': {'Status': {}},
            'Power': {'Status': {}},
            'Reboot': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Channel'], 'Status': {}},
            'Zoom': {'Status': {}},
        }

        self.Authentication = False
        welcome_msg = b''.join([b'Welcome ', self.deviceUsername.encode(encoding='iso-8859-1'), b'\r\n> '])

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'login: '), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password: '), self.__MatchPassword, None)
            self.AddMatchString(compile(welcome_msg), self.__MatchLoginSuccessful, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLoginSuccessful(self, match, tag):
        self.Authentication = True

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            'Master': 'master',
            'Built-in Microphone': 'mic_input',
            'External Microphone': 'easy_mic_1',
            'Incoming USB Stream': 'usb_playback',
            'Speaker': 'speaker',
            'Outbound USB Stream': 'usb_record',
            'Outbound IP Stream Left': 'ip_out_left',
            'Outbound IP Stream Right': 'ip_out_right',
        }

        ValueStateValues = ('On', 'Off')

        channel = qualifier['Channel']
        if value in ValueStateValues and channel in ChannelStates:
            AudioMuteCmdString = 'audio {} mute {}\r'.format(ChannelStates[channel], value.lower())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'Master': 'master',
            'Built-in Microphone': 'mic_input',
            'External Microphone': 'easy_mic_1',
            'Incoming USB Stream': 'usb_playback',
            'Speaker': 'speaker',
            'Outbound USB Stream': 'usb_record',
            'Outbound IP Stream Left': 'ip_out_left',
            'Outbound IP Stream Right': 'ip_out_right',
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            AudioMuteCmdString = 'audio {} mute get\r'.format(ChannelStates[channel])
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = res.split(':')[1].strip().title()
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetAutoWhiteBalance(self, value, qualifier):

        ValueStateValues = ('On', 'Off')

        if value in ValueStateValues:
            AutoWhiteBalanceCmdString = 'camera ccu set auto_white_balance {}\r'.format(value.lower())
            self.__SetHelper('AutoWhiteBalance', AutoWhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoWhiteBalance')

    def UpdateAutoWhiteBalance(self, value, qualifier):

        AutoWhiteBalanceCmdString = 'camera ccu get auto_white_balance\r'
        res = self.__UpdateHelper('AutoWhiteBalance', AutoWhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = res.split()[1].strip().title()
                self.WriteStatus('AutoWhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto White Balance: Invalid/unexpected response'])

    def SetBacklightCompensation(self, value, qualifier):

        ValueStateValues = ('On', 'Off')

        if value in ValueStateValues:
            BacklightCompensationCmdString = 'camera ccu set backlight_compensation {}\r'.format(value.lower())
            self.__SetHelper('BacklightCompensation', BacklightCompensationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightCompensation')

    def UpdateBacklightCompensation(self, value, qualifier):

        BacklightCompensationCmdString = 'camera ccu get backlight_compensation\r'
        res = self.__UpdateHelper('BacklightCompensation', BacklightCompensationCmdString, value, qualifier)
        if res:
            try:
                value = res.split()[1].strip().title()
                self.WriteStatus('BacklightCompensation', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight Compensation: Invalid/unexpected response'])

    def SetDewarp(self, value, qualifier):

        ValueStateValues = ('Off', 'Half', 'Full')

        if value in ValueStateValues:
            DewarpCmdString = 'camera dewarp set {}\r'.format(value.lower())
            self.__SetHelper('Dewarp', DewarpCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDewarp')

    def UpdateDewarp(self, value, qualifier):

        DewarpCmdString = 'camera dewarp get\r'
        res = self.__UpdateHelper('Dewarp', DewarpCmdString, value, qualifier)
        if res:
            try:
                value = res.split(':')[1].strip().title()
                self.WriteStatus('Dewarp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Dewarp: Invalid/unexpected response'])

    def SetIndicatorLight(self, value, qualifier):

        ValueStateValues = ('On', 'Off')

        if value in ValueStateValues:
            IndicatorLightCmdString = 'camera led {}\r'.format(value.lower())
            self.__SetHelper('IndicatorLight', IndicatorLightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIndicatorLight')

    def UpdateIndicatorLight(self, value, qualifier):

        IndicatorLightCmdString = 'camera led get\r'
        res = self.__UpdateHelper('IndicatorLight', IndicatorLightCmdString, value, qualifier)
        if res:
            try:
                value = res.split(':')[1].strip().title()
                self.WriteStatus('IndicatorLight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Indicator Light: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'off',
            'Off': 'on',
        }

        if value in ValueStateValues:
            PowerCmdString = 'camera standby {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'off': 'On',
            'on': 'Off',
        }

        PowerCmdString = 'camera standby get\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split(':')[1].strip()]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'system reboot\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = ('On', 'Off')

        if value in ValueStateValues:
            VideoMuteCmdString = 'video mute {}\r'.format(value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'video mute get\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = res.split(':')[1].strip().title()
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ChannelStates = {
            'Master': 'master',
            'Built-in Microphone': 'mic_input',
            'External Microphone': 'easy_mic_1',
            'Incoming USB Stream': 'usb_playback',
            'Speaker': 'speaker',
            'Outbound USB Stream': 'usb_record',
            'Outbound IP Stream Left': 'ip_out_left',
            'Outbound IP Stream Right': 'ip_out_right',
        }

        ValueStateValues = ('Up', 'Down')

        channel = qualifier['Channel']
        if value in ValueStateValues and channel in ChannelStates:
            VolumeCmdString = 'audio {} volume {}\r'.format(ChannelStates[channel], value.lower())
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def SetZoom(self, value, qualifier):

        ValueStateValues = ('1x', '1.5x', '2x')

        if value in ValueStateValues:
            ZoomCmdString = 'camera zoom set {}\r'.format(value)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        ZoomCmdString = 'camera zoom get\r'
        res = self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)
        if res:
            try:
                value = res.split(':')[1].strip()
                self.WriteStatus('Zoom', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zoom: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authentication:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
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

        self.Authentication = False

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

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