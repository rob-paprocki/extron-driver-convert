from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.deviceUsername = 'roomcontrol'
        self.devicePassword = 'Yamaha-CS-700'
        self.Models = {}

        self.Commands = {
            'Answer': {'Status': {}},
            'ApplyCameraDefaults': {'Status': {}},
            'MicMute': {'Status': {}},
            'BacklightComp': {'Status': {}},
            'BluetoothCallStatus': {'Status': {}},
            'CameraMute': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'Dial': {'Parameters':['VoIP Line ID'], 'Status': {}},
            'DialerConnectionMode': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Parameters':['VoIP Line ID'], 'Status': {}},
            'HangUp': {'Status': {}},
            'Hold': {'Status': {}},
            'Join': {'Parameters':['VoIP Line ID 1','VoIP Line ID 2','USB','Bluetooth'], 'Status': {}},
            'Pan': {'Status': {}},
            'PlayRingTone': {'Status': {}},
            'Resume': {'Status': {}},
            'RingerVolume': {'Status': {}},
            'SpeakerVolume': {'Status': {}},
            'Swap': {'Parameters':['Held Line ID'], 'Status': {}},
            'Tilt': {'Status': {}},
            'Transfer': {'Parameters':['Source Line ID'], 'Status': {}},
            'USBCallStatus': {'Status': {}},
            'USBConnectionStatus': {'Status': {}},
            'VoIPCallerName': {'Parameters':['VoIP Line ID'], 'Status': {}},
            'VoIPCallerNumber': {'Parameters':['VoIP Line ID'], 'Status': {}},
            'VoIPCallStatus': {'Parameters':['VoIP Line ID'], 'Status': {}},
            'Zoom': {'Status': {}}
            }
        self.authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'camera-backlight ([0-5])\r\n'), self.__MatchBacklightComp, None)
            self.AddMatchString(re.compile(b'status bt (idle|active|incoming|inactive|onhold|connected-in-conf)\r\n'), self.__MatchBluetoothCallStatus, None)
            self.AddMatchString(re.compile(b'dialer-connection-mode (ble|rc|disconnected)\r\n'), self.__MatchDialerConnectionMode, None)
            self.AddMatchString(re.compile(b'do-not-disturb ([01])\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(re.compile(b'(mute|camera-mute) ([01])\r\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'camera-pan (-?\d{1,2})\r\n'), self.__MatchPan, None)
            self.AddMatchString(re.compile(b'ringer-volume (\d{1,2})\r\n'), self.__MatchRingerVolume, None)
            self.AddMatchString(re.compile(b'speaker-volume (\d{1,2})\r\n'), self.__MatchSpeakerVolume, None)
            self.AddMatchString(re.compile(b'camera-tilt (-?\d{1,2})\r\n'), self.__MatchTilt, None)
            self.AddMatchString(re.compile(b'status usb (idle|active|incoming|inactive|onhold|connected-in-conf)\r\n'), self.__MatchUSBCallStatus, None)
            self.AddMatchString(re.compile(b'usb-conn-status ([01])\r\n'), self.__MatchUSBConnectionStatus, None)
            self.AddMatchString(re.compile(b'call-info ([1-3]) ([\S ]+) (\S+) (idle|incoming|calling|failed|connected|onhold|connected-in-conf|disconnected|update|missed)\r\n'), self.__MatchVoIPCallStatus, 'query')
            self.AddMatchString(re.compile(b'status ([1-3]) (idle|incoming|calling|failed|connected|onhold|connected-in-conf|disconnected|update|missed)\r\n'), self.__MatchVoIPCallStatus, 'unsolicited')
            self.AddMatchString(re.compile(b'camera-zoom (\d{1,2})\r\n'), self.__MatchZoom, None)
            self.AddMatchString(re.compile(b'(command syntax error)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)  # removed 'cs700 ' as some older firmware uses 'cannonball login' for backward compatibility
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Welcome to the CS-700 IP Management Interface\r\n'), self.__MatchLoginSuccessful, None)
            self.AddMatchString(re.compile(b'Login incorrect\r\n'), self.__MatchLoginFailed, None)

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self.deviceUsername + '\r\n')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLoginSuccessful(self, match, tag):

        self.authenticated = True
        self.SetNotification(None, None)

    def __MatchLoginFailed(self, match, tag):

        self.authenticated = False
        self.Error(['Login procedure failed. Check Username and Password.'])

    def SetNotification(self, value, qualifier):
        self.Send('regnotify\r')

    def SetAnswer(self, value, qualifier):

        ValueStateValues = {
            'VoIP Line 1': '1',
            'VoIP Line 2': '2',
            'USB': 'usb',
            'Bluetooth': 'bt'
        }
        AnswerCmdString = 'answer {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Answer', AnswerCmdString, value, qualifier)

    def SetApplyCameraDefaults(self, value, qualifier):

        ApplyCameraDefaultsCmdString = 'cam-apply-defaults\r'
        self.__SetHelper('ApplyCameraDefaults', ApplyCameraDefaultsCmdString, value, qualifier)

    def SetBacklightComp(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        BacklightCompCmdString = 'set camera-backlight {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('BacklightComp', BacklightCompCmdString, value, qualifier)

    def UpdateBacklightComp(self, value, qualifier):

        BacklightCompCmdString = 'get camera-backlight\r'
        self.__UpdateHelper('BacklightComp', BacklightCompCmdString, value, qualifier)

    def __MatchBacklightComp(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BacklightComp', value, None)

    def UpdateBluetoothCallStatus(self, value, qualifier):

        BluetoothCallStatusCmdString = 'get status bt\r'
        self.__UpdateHelper('BluetoothCallStatus', BluetoothCallStatusCmdString, value, qualifier)

    def __MatchBluetoothCallStatus(self, match, tag):

        ValueStateValues = {
            'idle': 'Idle',
            'active': 'Active',
            'incoming': 'Incoming',
            'inactive': 'Inactive',
            'connected': 'Connected',
            'onhold': 'On Hold',
            'connected-in-conf': 'Connected-In-Conference'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BluetoothCallStatus', value, None)

    def SetCameraMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        CameraMuteCmdString = 'set camera-mute {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CameraMute', CameraMuteCmdString, value, qualifier)

    def UpdateCameraMute(self, value, qualifier):

        CameraMuteCmdString = 'get camera-mute\r'
        self.__UpdateHelper('CameraMute', CameraMuteCmdString, value, qualifier)

    def SetDial(self, value, qualifier):

        voip_id = qualifier['VoIP Line ID']
        numberString = value
        if numberString and 1 <= int(voip_id) <= 3:
            DialCmdString = 'dial {0} {1}\r'.format(voip_id, numberString)
            self.__SetHelper('Dial', DialCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDial')

    def SetDialerConnectionMode(self, value, qualifier):

        ValueStateValues = {
            'Bluetooth': 'ble',
            'Room Control': 'rc',
            'Disconnected': 'disconnected'
        }

        DialerConnectionModeCmdString = 'set dialer-connection-mode {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('DialerConnectionMode', DialerConnectionModeCmdString, value, qualifier)

    def UpdateDialerConnectionMode(self, value, qualifier):

        DialerConnectionModeCmdString = 'get dialer-connection-mode\r'
        self.__UpdateHelper('DialerConnectionMode', DialerConnectionModeCmdString, value, qualifier)

    def __MatchDialerConnectionMode(self, match, tag):

        ValueStateValues = {
            'ble': 'Bluetooth',
            'rc': 'Room Control',
            'disconnected': 'Disconnected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DialerConnectionMode', value, None)

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        DoNotDisturbCmdString = 'set do-not-disturb {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        DoNotDisturbCmdString = 'get do-not-disturb\r'
        self.__UpdateHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def __MatchDoNotDisturb(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DoNotDisturb', value, None)

    def SetDTMF(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '*': '*',
            '#': '#',
            'End Tone': '-'  # page 119 of CS-700 API (002).pdf
        }
        voip_id = qualifier['VoIP Line ID']
        if 1 <= int(voip_id) <= 3:
            DTMFCmdString = 'set dtmf {0} {1}\r'.format(voip_id, ValueStateValues[value])
            self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetHangUp(self, value, qualifier):

        ValueStateValues = {
            'VoIP Line 1': '1',
            'VoIP Line 2': '2',
            'VoIP Line 3': '3',
            'USB': 'usb',
            'Bluetooth': 'bt',
        }

        HangUpCmdString = 'hangup {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('HangUp', HangUpCmdString, value, qualifier)

    def SetHold(self, value, qualifier):

        ValueStateValues = {
            'VoIP Line 1': '1',
            'VoIP Line 2': '2',
            'USB': 'usb',
            'Bluetooth': 'bt',
            'All': 'all'
        }

        HoldCmdString = 'hold {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Hold', HoldCmdString, value, qualifier)

    def SetJoin(self, value, qualifier):

        VoIPLineID1States = {
            'Join': '1',
            'Separate': '0'
        }[qualifier['VoIP Line ID 1']]

        VoIPLineID2States = {
            'Join': '1',
            'Separate': '0'
        }[qualifier['VoIP Line ID 2']]

        USBStates = {
            'Join': '1',
            'Separate': '0'
        }[qualifier['USB']]

        BluetoothStates = {
            'Join': '1',
            'Separate': '0'
        }[qualifier['Bluetooth']]

        JoinCmdString = 'join 1 {0} 2 {1} usb {2} bt {3}\r'.format(VoIPLineID1States, VoIPLineID2States, USBStates, BluetoothStates)
        self.__SetHelper('Join', JoinCmdString, value, qualifier)

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MicMuteCmdString = 'set mute {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)

    def UpdateMicMute(self, value, qualifier):

        MicMuteCmdString = 'get mute\r'
        self.__UpdateHelper('MicMute', MicMuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        value = ValueStateValues[match.group(2).decode()]
        if match.group(1).decode() == 'mute':  # Mic Mute response
            self.WriteStatus('MicMute', value, None)
        else:  # Camera Mute response
            self.WriteStatus('CameraMute', value, None)

    def SetPan(self, value, qualifier):

        ValueConstraints = {
            'Min': -30,
            'Max': 30
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PanCmdString = 'set camera-pan {0}\r'.format(value)
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def UpdatePan(self, value, qualifier):

        PanCmdString = 'get camera-pan\r'
        self.__UpdateHelper('Pan', PanCmdString, value, qualifier)

    def __MatchPan(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Pan', value, None)

    def SetPlayRingTone(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        PlayRingToneCmdString = 'play ring-tone {}\r'.format(ValueStateValues[value])
        self.__SetHelper('PlayRingTone', PlayRingToneCmdString, value, qualifier)

    def SetResume(self, value, qualifier):

        ValueStateValues = {
            'VoIP Line 1': '1',
            'VoIP Line 2': '2',
            'USB': 'usb',
            'Bluetooth': 'bt'
        }

        ResumeCmdString = 'resume {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Resume', ResumeCmdString, value, qualifier)

    def SetRingerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 18
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            RingerVolumeCmdString = 'set ringer-volume {0}\r'.format(value)
            self.__SetHelper('RingerVolume', RingerVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRingerVolume')

    def UpdateRingerVolume(self, value, qualifier):

        RingerVolumeCmdString = 'get ringer-volume\r'
        self.__UpdateHelper('RingerVolume', RingerVolumeCmdString, value, qualifier)

    def __MatchRingerVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('RingerVolume', value, None)

    def SetSpeakerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 18
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SpeakerVolumeCmdString = 'set speaker-volume {0}\r'.format(value)
            self.__SetHelper('SpeakerVolume', SpeakerVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerVolume')

    def UpdateSpeakerVolume(self, value, qualifier):

        SpeakerVolumeCmdString = 'get speaker-volume\r'
        self.__UpdateHelper('SpeakerVolume', SpeakerVolumeCmdString, value, qualifier)

    def __MatchSpeakerVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('SpeakerVolume', value, None)

    def SetSwap(self, value, qualifier):

        HeldLineIDStates = {
            'VoIP Line 1': '1',
            'VoIP Line 2': '2',
            'USB': 'usb',
            'Bluetooth': 'bt'
        }

        ValueStateValues = {
            'VoIP Line 1': '1',
            'VoIP Line 2': '2',
            'USB': 'usb',
            'Bluetooth': 'bt'
        }

        SwapCmdString = 'swap {0} {1}\r'.format(HeldLineIDStates[qualifier['Held Line ID']], ValueStateValues[value])
        self.__SetHelper('Swap', SwapCmdString, value, qualifier)

    def SetTilt(self, value, qualifier):

        ValueConstraints = {
            'Min': -18,
            'Max': 18
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TiltCmdString = 'set camera-tilt {0}\r'.format(value)
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def UpdateTilt(self, value, qualifier):

        TiltCmdString = 'get camera-tilt\r'
        self.__UpdateHelper('Tilt', TiltCmdString, value, qualifier)

    def __MatchTilt(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Tilt', value, None)

    def SetTransfer(self, value, qualifier):

        SourceLineIDStates = {
            'VoIP Line 1': '1',
            'VoIP Line 2': '2',
        }

        TransferCmdString = 'transfer {0} 3\r'.format(SourceLineIDStates[qualifier['Source Line ID']])
        self.__SetHelper('Transfer', TransferCmdString, value, qualifier)

    def UpdateUSBCallStatus(self, value, qualifier):

        USBCallStatusCmdString = 'get status usb\r'
        self.__UpdateHelper('USBCallStatus', USBCallStatusCmdString, value, qualifier)

    def __MatchUSBCallStatus(self, match, tag):

        ValueStateValues = {
            'idle': 'Idle',
            'active': 'Active',
            'incoming': 'Incoming',
            'inactive': 'Inactive',
            'connected': 'Connected',
            'onhold': 'On Hold',
            'connected-in-conf': 'Connected-In-Conference'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBCallStatus', value, None)

    def UpdateUSBConnectionStatus(self, value, qualifier):

        USBConnectionStatusCmdString = 'get usb-conn-status\r'
        self.__UpdateHelper('USBConnectionStatus', USBConnectionStatusCmdString, value, qualifier)

    def __MatchUSBConnectionStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Connected',
            '0': 'Disconnected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBConnectionStatus', value, None)

    def UpdateVoIPCallerName(self, value, qualifier):

        self.UpdateVoIPCallStatus(value, qualifier)

    def UpdateVoIPCallerNumber(self, value, qualifier):

        self.UpdateVoIPCallStatus(value, qualifier)

    def UpdateVoIPCallStatus(self, value, qualifier):

        if qualifier['VoIP Line ID'] in ['1', '2', '3']:
            VoIPCallStatusCmdString = 'get call-info {0}\r'.format(qualifier['VoIP Line ID'])
            self.__UpdateHelper('VoIPCallStatus', VoIPCallStatusCmdString, value, qualifier)
        else:
            self.Discard("Invalid Command for UpdateVoIPCall")

    def __MatchVoIPCallStatus(self, match, tag):

        ValueStateValues = {
            'idle': 'Idle',
            'incoming': 'Incoming',
            'calling': 'Calling',
            'failed': 'Failed',
            'connected': 'Connected',
            'onhold': 'On Hold',
            'connected-in-conf': 'Connected-In-Conference',
            'disconnected': 'Disconnected',
            'update': 'Update',
            'missed': 'Missed'
        }

        voip_id = match.group(1).decode()
        if tag == 'query':
            voip_name = match.group(2).decode()
            voip_number = match.group(3).decode()
            value = ValueStateValues[match.group(4).decode()]
            self.WriteStatus('VoIPCallStatus', value, {'VoIP Line ID': voip_id})
            self.WriteStatus('VoIPCallerName', voip_name, {'VoIP Line ID': voip_id})
            self.WriteStatus('VoIPCallerNumber', voip_number, {'VoIP Line ID': voip_id})
        else:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('VoIPCallStatus', value, {'VoIP Line ID': voip_id})

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 22
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoomCmdString = 'set camera-zoom {0}\r'.format(value)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        ZoomCmdString = 'get camera-zoom\r'
        self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)

    def __MatchZoom(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Zoom', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)
        

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.authenticated:
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
        self.counter = 0

        self.Error([match.group(1).decode().title()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.authenticated = False
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
        index = 0    # Start of possible good data

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
