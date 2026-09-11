from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CDStatus': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Random': {'Status': {}},
            'Repeat': {'Status': {}},
            'TimeStatus': {'Status': {}},
            'TrackNumber': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PC1000R--> (Status: CD In Standby)|Device: (CD Player|USB|SD)\n'), self.__MatchCDStatus, None)
            self.AddMatchString(re.compile(b'PC1000R--> CD Mute (On|Off)\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'PC1000R--> CD (On|Off)\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'PC1000R--> Random Mode (On|Off)\n'), self.__MatchRandom, None)
            self.AddMatchString(re.compile(b'PC1000R--> Repeat (1 |Off|All)\n'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'PC1000R--> Time: (\d{2}:\d{2})\n'), self.__MatchTimeStatus, None)
            self.AddMatchString(re.compile(b'PC1000R--> [\S]+: ?([0-9]{1,4})\n'), self.__MatchTrackNumber, None)
            self.AddMatchString(re.compile(b'PC1000R--> (Play|Stop|Pause|Eject Command|Skip Next|Skip Back|Fast Play Forward|Fast Play Backward)\n'), self.__MatchTransport, None)

    def UpdateCDStatus(self, value, qualifier):

        CDStatusCmdString = 'STATUS'
        self.__UpdateHelper('CDStatus', CDStatusCmdString, value, qualifier)

    def __MatchCDStatus(self, match, tag):

        if match.group(1):
            value = match.group(1).decode()
        elif match.group(2):
            value = match.group(2).decode()

        self.WriteStatus('CDStatus', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = 'INPUT'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'CD MUTE ON',
            'Off': 'CD MUTE OFF'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Power', value, None)

    def SetRandom(self, value, qualifier):

        ValueStateValues = {
            'Off': 'RANDOM OFF',
            'On': 'RANDOM ON',
        }

        RandomCmdString = ValueStateValues[value]
        self.__SetHelper('Random', RandomCmdString, value, qualifier)

    def __MatchRandom(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Random', value, None)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'One': 'REPEAT 1',
            'All': 'REPEAT ALL',
            'Off': 'REPEAT OFF',
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

    def __MatchTimeStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeStatus', value, None)

    def SetTrackNumber(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 4095
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrackNumberCmdString = 'TRACK {0}'.format(value)
            self.__SetHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackNumber')

    def __MatchTrackNumber(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 4095:
            self.WriteStatus('TrackNumber', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': 'PLAY',
            'Pause': 'PAUSE',
            'Stop': 'STOP',
            'Eject': 'EJECT',
            'Previous': 'SKIP-',
            'Next': 'SKIP+',
            'Fast Forward': 'FAST+',
            'Rewind': 'FAST-'
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
            'Fast Play Backward': 'Rewind',
            'Fast Play Forward': 'Fast Forward',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Transport', value, None)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 'VOL+',
            'Down': 'VOL-',
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
            raise KeyError('Invalid command for ReadStatus: ' + command)

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
