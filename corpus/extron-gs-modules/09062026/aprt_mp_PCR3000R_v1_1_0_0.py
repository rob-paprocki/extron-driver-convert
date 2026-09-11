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
            'Band': {'Status': {}},
            'CD': {'Status': {}},
            'CDMute': {'Status': {}},
            'CDStatus': {'Status': {}},
            'DABStatus': {'Status': {}},
            'Info': {'Status': {}},
            'Input': {'Status': {}},
            'MonoStereo': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Random': {'Status': {}},
            'Repeat': {'Status': {}},
            'Scan': {'Status': {}},
            'TimeStatus': {'Status': {}},
            'Track': {'Status': {}},
            'Transport': {'Status': {}},
            'Tuner': {'Status': {}},
            'TunerMode': {'Status': {}},
            'TunerMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PCR3000R--> CD (On|Off)\n'), self.__MatchCD, None)
            self.AddMatchString(re.compile(b'PCR3000R--> CD Mute (On|Off)\n'), self.__MatchCDMute, None)
            self.AddMatchString(re.compile(b'PCR3000R--> (Status: CD In Standby)|(Device: (CD Player|USB|SD))\n'), self.__MatchCDStatus, None)
            self.AddMatchString(re.compile(b'\n?(Status: DAB In Standby)|(Bluetooth)|(\d+\.\d+.+?)|(Scanning).+?|(NPO .*)|(No DAB Station)|(Manual Tune|DRC|Station Order|Prune|Full Scan|Audio Setting|Scan Setting|System)\n?'), self.__MatchDABStatus, None)
            self.AddMatchString(re.compile(b'PCR3000R--> Preset: ([0-9]{1,2})\n'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'PCR3000R--> Random Mode (On|Off)\n'), self.__MatchRandom, None)
            self.AddMatchString(re.compile(b'PCR3000R--> Repeat (1 |All|Off)\n'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'PCR3000R--> Time: (\d{2}:\d{2})\n'), self.__MatchTimeStatus, None)
            self.AddMatchString(re.compile(b'PCR3000R--> Track: ([0-9]{4})\n'), self.__MatchTrack, None)
            self.AddMatchString(re.compile(b'PCR3000R--> (Play|Pause|Stop|Eject Command|Skip Next|Skip Back|Fast Play Forward|Fast Play Backward)\n'), self.__MatchTransport, None)
            self.AddMatchString(re.compile(b'PCR3000R--> DAB (On|Off)\n'), self.__MatchTunerMode, None)
            self.AddMatchString(re.compile(b'PCR3000R--> DAB Mute (On|Off)\n'), self.__MatchTunerMute, None)

    def SetBand(self, value, qualifier):

        BandCmdString = 'BAND'
        self.__SetHelper('Band', BandCmdString, value, qualifier)

    def SetCD(self, value, qualifier):

        ValueStateValues = {
            'On': 'CD ON',
            'Off': 'CD OFF'
        }

        CDCmdString = ValueStateValues[value]
        self.__SetHelper('CD', CDCmdString, value, qualifier)

    def __MatchCD(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CD', value, None)

    def SetCDMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'CD MUTE ON',
            'Off': 'CD MUTE OFF'
        }

        CDMuteCmdString = ValueStateValues[value]
        self.__SetHelper('CDMute', CDMuteCmdString, value, qualifier)

    def __MatchCDMute(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CDMute', value, None)

    def UpdateCDStatus(self, value, qualifier):

        CDStatusCmdString = 'STATUS CD'
        self.__UpdateHelper('CDStatus', CDStatusCmdString, value, qualifier)

    def __MatchCDStatus(self, match, tag):

        if match.group(1):
            value = match.group(1).decode()
        elif match.group(2):
            value = match.group(2).decode()
        self.WriteStatus('CDStatus', value, None)

    def UpdateDABStatus(self, value, qualifier):

        DABStatusCmdString = 'STATUS DAB'
        self.__UpdateHelper('DABStatus', DABStatusCmdString, value, qualifier)

    def __MatchDABStatus(self, match, tag):

        value = ''
        if match.group(1):
            value = match.group(1).decode()
        elif match.group(2):
            value = 'Bluetooth Mode'
        elif match.group(3) or match.group(5):
            value = 'FM Mode'
        elif match.group(4):
            value = 'Scanning Mode'
        elif match.group(6):
            value = match.group(6).decode()
        elif match.group(7):
            value = 'DAB in Menu'
        if value:
            self.WriteStatus('DABStatus', value, None)

    def SetInfo(self, value, qualifier):

        InfoCmdString = 'INFO'
        self.__SetHelper('Info', InfoCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = 'INPUT'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMonoStereo(self, value, qualifier):

        MonoStereoCmdString = 'ENTER'
        self.__SetHelper('MonoStereo', MonoStereoCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': 'PRESET 1',
            '2': 'PRESET 2',
            '3': 'PRESET 3',
            '4': 'PRESET 4',
            '5': 'PRESET 5',
            '6': 'PRESET 6',
            '7': 'PRESET 7',
            '8': 'PRESET 8',
            '9': 'PRESET 9',
            '10': 'PRESET 10'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('PresetRecall', value, None)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': 'SAVE 1',
            '2': 'SAVE 2',
            '3': 'SAVE 3',
            '4': 'SAVE 4',
            '5': 'SAVE 5',
            '6': 'SAVE 6',
            '7': 'SAVE 7',
            '8': 'SAVE 8',
            '9': 'SAVE 9',
            '10': 'SAVE 10'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetRandom(self, value, qualifier):

        ValueStateValues = {
            'On': 'RANDOM ON',
            'Off': 'RANDOM OFF'
        }

        RandomCmdString = ValueStateValues[value]
        self.__SetHelper('Random', RandomCmdString, value, qualifier)

    def __MatchRandom(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Random', value, None)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Off': 'REPEAT OFF',
            'One': 'REPEAT 1',
            'All': 'REPEAT ALL'
        }

        RepeatCmdString = ValueStateValues[value]
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def __MatchRepeat(self, match, tag):

        ValueStateValues = {
            'Off': 'Off',
            '1 ': 'One',
            'All': 'All'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Repeat', value, None)

    def SetScan(self, value, qualifier):

        ValueStateValues = {
            'Next': 'AUTO+',
            'Previous': 'AUTO-'
        }

        ScanCmdString = ValueStateValues[value]
        self.__SetHelper('Scan', ScanCmdString, value, qualifier)

    def __MatchTimeStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeStatus', value, None)

    def SetTrack(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 4095
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrackCmdString = 'TRACK {0}'.format(value)
            self.__SetHelper('Track', TrackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrack')

    def __MatchTrack(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Track', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': 'PLAY',
            'Stop': 'STOP',
            'Pause': 'PAUSE',
            'Eject': 'EJECT',
            'Next': 'SKIP+',
            'Previous': 'SKIP-',
            'Fast Forward': 'FAST+',
            'Fast Backward': 'FAST-'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __MatchTransport(self, match, tag):

        ValueStateValues = {
            'Play': 'Play',
            'Stop': 'Stop',
            'Pause': 'Pause',
            'Eject Command': 'Eject',
            'Skip Next': 'Next',
            'Skip Back': 'Previous',
            'Fast Play Backward': 'Fast Backward',
            'Fast Play Forward': 'Fast Forward',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Transport', value, None)

    def SetTuner(self, value, qualifier):

        ValueStateValues = {
            'Up': 'TUNE+',
            'Down': 'TUNE-'
        }

        TunerCmdString = ValueStateValues[value]
        self.__SetHelper('Tuner', TunerCmdString, value, qualifier)

    def SetTunerMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'DAB ON',
            'Off': 'DAB OFF'
        }

        TunerModeCmdString = ValueStateValues[value]
        self.__SetHelper('TunerMode', TunerModeCmdString, value, qualifier)

    def __MatchTunerMode(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TunerMode', value, None)

    def SetTunerMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'DAB MUTE ON',
            'Off': 'DAB MUTE OFF'
        }

        TunerMuteCmdString = ValueStateValues[value]
        self.__SetHelper('TunerMute', TunerMuteCmdString, value, qualifier)

    def __MatchTunerMute(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TunerMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 'VOL+',
            'Down': 'VOL-'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
