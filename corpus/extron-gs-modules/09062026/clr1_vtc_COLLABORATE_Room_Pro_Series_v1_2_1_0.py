from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from collections import OrderedDict


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
        self.LocalContactListDisplayCount = 5
        self.deviceUsername = None
        self.devicePassword = None

        self.Models = {
            'COLLABORATE Room Pro 500': self.clr1_12_1219_other,
            'COLLABORATE Room Pro 600': self.clr1_12_1219_other,
            'COLLABORATE Room Pro 900': self.clr1_12_1219_other,
            'COLLABORATE Room Pro 300': self.clr1_12_1219_300,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CameraNearFar': {'Status': {}},
            'CameraSelect': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Parameters': ['Call Type', 'Bandwidth'], 'Status': {}},
            'HookStatus': {'Status': {}},
            'Keypad': {'Status': {}},
            'LocalContactListNavigation': {'Status': {}},
            'LocalContactListResults': {'Parameters': ['Position'], 'Status': {}},
            'LocalContactListResultSet': {'Parameters': ['Position'], 'Status': {}},
            'LocalContactListUpdate': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Microphone': {'Status': {}},
            'Multicast': {'Status': {}},
            'PanTilt': {'Status': {}},
            'PhoneBook': {'Status': {}},
            'PresetRestore': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Recording': {'Status': {}},
            'RiseException': {'Status': {}},
            'SecurityMode': {'Status': {}},
            'ShareHDMI': {'Parameters': ['Input'], 'Status': {}},
            'ShareLaptop': {'Status': {}},
            'ShareWireless': {'Status': {}},
            'Shutdown': {'Status': {}},
            'Speaker': {'Status': {}},
            'Status': {'Status': {}},
            'Streaming': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Username:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'get_property autoanswer (on|off)\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(re.compile(b'(conversation_established|conversation_terminated|participant_added|participant_removed|incoming_call)\n'), self.__MatchHookStatus, None)
            self.AddMatchString(re.compile(b'get_property mic (on|off)\n'), self.__MatchMicrophone, None)
            self.AddMatchString(re.compile(b'get_property rise_exception (on|off)\n'), self.__MatchRiseException, None)
            self.AddMatchString(re.compile(b'get_property security_mode (auto|none)\n'), self.__MatchSecurityMode, None)
            self.AddMatchString(re.compile(b'get_property speaker (on|off)\n'), self.__MatchSpeaker, None)
            self.AddMatchString(re.compile(b'get_property volume ([0-9]{1,3})\n'), self.__MatchVolume, None)

        self.LocalContactPattern = re.compile('=>contact (\d+) (.*)\n\r')
        self.ContactNameDict = OrderedDict()
        self.DialfromList = False

    @property
    def LocalContactListDisplayCount(self):
        return self._LocalContactListDisplayCount

    @LocalContactListDisplayCount.setter
    def LocalContactListDisplayCount(self, value):
        if 1 <= int(value) <= 10:
            self._LocalContactListDisplayCount = int(value)
            self.ContactListDirectory = Directory(self._LocalContactListDisplayCount, 'LocalContactListResults', filler='')
            self.ContactListDirectory.write_status_function = self.WriteStatus
        else:
            self.Error('Local Contact List Display Count should be a value between 1 to 10.')

    def SetLocalContactListNavigation(self, value, qualifier):

        if value == 'Up':
            self.ContactListDirectory.scroll_up(1)
        elif value == 'Down':
            self.ContactListDirectory.scroll_down(1)
        elif value == 'Page Up':
            self.ContactListDirectory.scroll_up(self._LocalContactListDisplayCount)
        elif value == 'Page Down':
            self.ContactListDirectory.scroll_down(self._LocalContactListDisplayCount)
        else:
            self.Discard('Invalid Command for SetLocalContactListNavigation')

    def SetLocalContactListUpdate(self, value, qualifier):

        LocalContactListRefreshCmdString = 'listcontacts\r\n'
        res = self.__SetHelperSync('LocalContactListUpdate', LocalContactListRefreshCmdString, value, qualifier)
        if res:
            self.ContactNameDict = OrderedDict(self.LocalContactPattern.findall(res.decode()))
            LocalList = []
            for i in self.ContactNameDict:
                temp = '{0} : {1}'.format(i, self.ContactNameDict[i])
                LocalList.append(temp)
            LocalList.append('***End of List***')

            self.ContactListDirectory.reset(LocalList)

    def SetLocalContactListResultSet(self, value, qualifier):

        entry = self.ReadStatus('LocalContactListResults', qualifier)
        if entry and '***End of List***' not in entry:
            number = entry.split(':')[0].strip()
            self.DialfromList = True
            qual = {
                'Number': number,
                'Call Type': qualifier['Call Type'],
                'Bandwidth': qualifier['Bandwidth']}
            self.SetHook('Dial', qual)

    def __MatchUsername(self, match, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'On': 'set autoanswer on\r\n',
            'Off': 'set autoanswer off\r\n'
        }

        AutoAnswerCmdString = ValueStateValues[value]
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerCmdString = 'get autoanswer\r\n'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoAnswer', value, None)

    def SetCameraNearFar(self, value, qualifier):

        CameraNearFarCmdString = 'remotecontrol 5\r\n'
        self.__SetHelper('CameraNearFar', CameraNearFarCmdString, value, qualifier)

    def SetCameraSelect(self, value, qualifier):

        if 1 <= int(value) <= 9:
            CameraSelectCmdString = 'change_camera {0}\r\n'.format(value)
            self.__SetHelper('CameraSelect', CameraSelectCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetCameraSelect')

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'Enable': 'donotdisturb enable\r\n',
            'Disable': 'donotdisturb disable\r\n'
        }

        DoNotDisturbCmdString = ValueStateValues[value]
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def SetDTMF(self, value, qualifier):

        if value in '0123456789#*':
            DTMFCmdString = 'dtmf {0}\r\n'.format(value)
            self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetHook(self, value, qualifier):

        CallTypeStates = {
            'LAN': 'lan',
            'ISDN': 'isdn',
            'Audio': 'audio',
            'None': ''
        }

        BandwidthStates = {
            '64': '64',
            '128': '128',
            '256': '256',
            '384': '384',
            '512': '512',
            '1024': '1024',
            '1532': '1532',
            '2048': '2048',
            '2560': '2560',
            '3072': '3072',
            '3584': '3584',
            '4096': '4096',
            '4608': '4608',
            '5120': '5120',
            '5632': '5632',
            '6144': '6144',
            'None': ''
        }
        
        if value == 'On':
            CommandString = 'hangup\r\n'
            self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Dial':
            calltype = CallTypeStates[qualifier['Call Type']]
            bandwidth = BandwidthStates[qualifier['Bandwidth']]
            if calltype != '' and bandwidth != '':
                number = qualifier['Number']
                if number:
                    if self.DialfromList is True:
                        dialString = 'dialcontact {0} {1} {2}\r\n'.format(number, calltype, bandwidth)
                    else:
                        dialString = 'dial {0} {1} {2}\r\n'.format(number, calltype, bandwidth)
                    self.__SetHelper('Hook', dialString, value, qualifier)
                    self.DialfromList = False
                else:
                    self.Discard('Invalid Command for SetHook')
            else:
                self.Discard('Invalid Command for SetHook')
        elif value == 'Accept':
            CommandString = 'accept\r\n'
            self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Reject':
            CommandString = 'reject\r\n'
            self.__SetHelper('Hook', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def __MatchHookStatus(self, match, tag):

        ValueStateValues = {
            'conversation_established': 'Connected',
            'conversation_terminated': 'Not in Call',
            'participant_added': 'Connecting',
            'participant_removed': 'Idling',
            'incoming_call': 'Ringing'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HookStatus', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '29',
            '2': '30',
            '3': '31',
            '4': '32',
            '5': '33',
            '6': '34',
            '7': '35',
            '8': '36',
            '9': '37',
            '0': '38',
            'Dot': '39',
            'Clear': '40'
        }
        KeypadCmdString = 'remotecontrol {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '20',
            'Down': '21',
            'Left': '19',
            'Right': '18',
            'Enter': '17',
            'Cancel': '22',
            'Menu': '14'
        }

        MenuNavigationCmdString = 'remotecontrol {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMicrophone(self, value, qualifier):

        ValueStateValues = {
            'On': 'set mic on\r\n',
            'Off': 'set mic off\r\n'
        }

        MicrophoneCmdString = ValueStateValues[value]
        self.__SetHelper('Microphone', MicrophoneCmdString, value, qualifier)

    def UpdateMicrophone(self, value, qualifier):

        MicrophoneCmdString = 'get mic\r\n'
        self.__UpdateHelper('Microphone', MicrophoneCmdString, value, qualifier)

    def __MatchMicrophone(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Microphone', value, None)

    def SetMulticast(self, value, qualifier):

        ValueStateValues = {
            'Start': 'multicast start\r\n',
            'Stop': 'multicast stop\r\n'
        }

        MulticastCmdString = ValueStateValues[value]
        self.__SetHelper('Multicast', MulticastCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': 'u',
            'Down': 'd',
            'Left': 'l',
            'Right': 'r',
            'Up-Left': 'ul',
            'Up-Right': 'ur',
            'Down-Left': 'dl',
            'Down-Right': 'dr',
        }

        if value == 'Stop':
            PanTiltCmdString = 'camerastop spt\r\n'
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            PanTiltCmdString = 'camerastart {0}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)

    def SetPhoneBook(self, value, qualifier):

        PhoneBookCmdString = 'remotecontrol 3\r\n'
        self.__SetHelper('PhoneBook', PhoneBookCmdString, value, qualifier)

    def SetPresetRestore(self, value, qualifier):

        if 1 <= int(value) <= self.numberOfPresets:
            PresetRestoreCmdString = 'camerapos restore {0}\r\n'.format(value)
            self.__SetHelper('PresetRestore', PresetRestoreCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetPresetRestore')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= self.numberOfPresets:
            PresetSaveCmdString = 'camerapos save {0}\r\n'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetPresetSave')

    def SetRecording(self, value, qualifier):

        ValueStateValues = {
            'Start': 'recording start\r\n',
            'Stop': 'recording stop\r\n'
        }

        RecordingCmdString = ValueStateValues[value]
        self.__SetHelper('Recording', RecordingCmdString, value, qualifier)

    def SetRiseException(self, value, qualifier):

        ValueStateValues = {
            'On': 'set rise_exception on\r\n',
            'Off': 'set rise_exception off\r\n'
        }

        RiseExceptionCmdString = ValueStateValues[value]
        self.__SetHelper('RiseException', RiseExceptionCmdString, value, qualifier)

    def UpdateRiseException(self, value, qualifier):

        RiseExceptionCmdString = 'get rise_exception\r\n'
        self.__UpdateHelper('RiseException', RiseExceptionCmdString, value, qualifier)

    def __MatchRiseException(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RiseException', value, None)

    def SetSecurityMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'auto',
            'None': 'none'
        }

        SecurityModeCmdString = 'set security_mode {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('SecurityMode', SecurityModeCmdString, value, qualifier)

    def UpdateSecurityMode(self, value, qualifier):

        SecurityModeCmdString = 'get security_mode\r\n'
        self.__UpdateHelper('SecurityMode', SecurityModeCmdString, value, qualifier)

    def __MatchSecurityMode(self, match, tag):

        ValueStateValues = {
            'auto': 'Auto',
            'none': 'None'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SecurityMode', value, None)

    def SetShareHDMI(self, value, qualifier):

        InputStates = {
            'HDMI 1': '1',
            'HDMI 2': '2'
        }

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop'
        }

        inputState = InputStates[qualifier['Input']]
        ShareHDMICmdString = 'sharehdmi{0} {1}\r\n'.format(inputState, ValueStateValues[value])
        self.__SetHelper('ShareHDMI', ShareHDMICmdString, value, qualifier)

    def SetShareLaptop(self, value, qualifier):

        ValueStateValues = {
            'Start': 'sharelaptop start\r\n',
            'Stop': 'sharelaptop stop\r\n'
        }
        ShareLaptopCmdString = ValueStateValues[value]
        self.__SetHelper('ShareLaptop', ShareLaptopCmdString, value, qualifier)

    def SetShareWireless(self, value, qualifier):

        ValueStateValues = {
            'Start': 'sharewireless start\r\n',
            'Stop': 'sharewireless stop\r\n'
        }
        ShareWirelessCmdString = ValueStateValues[value]
        self.__SetHelper('ShareWireless', ShareWirelessCmdString, value, qualifier)

    def SetShutdown(self, value, qualifier):

        ValueStateValues = {
            'Shutdown': 'shutdown\r\n',
            'Restart': 'restart\r\n'
        }

        ShutdownCmdString = ValueStateValues[value]
        self.__SetHelper('Shutdown', ShutdownCmdString, value, qualifier)

    def SetSpeaker(self, value, qualifier):

        ValueStateValues = {
            'On': 'set speaker on\r\n',
            'Off': 'set speaker off\r\n'
        }
        SpeakerCmdString = ValueStateValues[value]
        self.__SetHelper('Speaker', SpeakerCmdString, value, qualifier)

    def UpdateSpeaker(self, value, qualifier):

        SpeakerCmdString = 'get speaker\r\n'
        self.__UpdateHelper('Speaker', SpeakerCmdString, value, qualifier)

    def __MatchSpeaker(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Speaker', value, None)

    def SetStatus(self, value, qualifier):

        StatusCmdString = 'remotecontrol 1\r\n'
        self.__SetHelper('Status', StatusCmdString, value, qualifier)

    def SetStreaming(self, value, qualifier):

        ValueStateValues = {
            'Start': 'streaming start\r\n',
            'Stop': 'streaming stop\r\n'
        }

        StreamingCmdString = ValueStateValues[value]
        self.__SetHelper('Streaming', StreamingCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'set volume {0}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get volume\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 'camerastart zi\r\n',
            'Wide': 'camerastart zo\r\n',
            'Stop': 'camerastop sz\r\n'
        }
        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __SetHelperSync(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
            return ''
        else:
            res = self.SendAndWait(commandstring, 10)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
                res = ''

            return res

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

    def clr1_12_1219_other(self):
        self.numberOfPresets = 9

    def clr1_12_1219_300(self):
        self.numberOfPresets = 18

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
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


def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_driver()
        return res

    return wrapper


class Directory:

    def __init__(self, display_count, write_function_name, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Position'
        self._qualifier_type = 'Enum'
        self._write_function_name = write_function_name

        self.entry_list = []

        self._start_index = 0
        self.auto_update = True
        self.filler = filler
        self.entry_function = lambda entry: entry

    @property
    def display_count(self):
        return self._display_count

    @property
    def qualifier_type(self):
        return self._qualifier_type

    @qualifier_type.setter
    def qualifier_type(self, value):
        if value in ('Enum', 'Number'):
            self._qualifier_type = value

    def write_to_driver(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name: position_value})

    def write_status_function(self, value, qualifier, context):
        pass

    @UseAutoUpdate
    def add_entry(self, entry):
        if isinstance(entry, list):
            self.entry_list.extend(entry)
        else:
            self.entry_list.append(entry)

    @UseAutoUpdate
    def reset(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()
        self._start_index = 0

    @UseAutoUpdate
    def remove_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list.pop(self._start_index + display_position - 1)
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list[self._start_index + display_position - 1]
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_displayed_entries(self):

        index = self._start_index
        while index <= self._start_index + self._display_count - 1:
            if index >= len(self.entry_list):
                yield self.filler, index + 1
            else:
                yield self.entry_list[index], index + 1

            index += 1

    def __display_position_check(self, position):

        return 0 < position <= self._display_count

    @UseAutoUpdate
    def scroll_up(self, step=1):
        if self._start_index - step >= 0:
            self._start_index -= step
        else:
            self._start_index = 0

    @UseAutoUpdate
    def scroll_down(self, step=1):
        if self._start_index + step < len(self.entry_list):
            self._start_index += step
        else:
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1
