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
            'AudioInput': {'Status': {}},
            'EDID': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Power': {'Status': {}},
            'Reset': {'Status': {}},
            'SourceStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoInput': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'AudioIN \?#00([1-8]);'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'EDID \?#00([1-6]);'), self.__MatchEDID, None)
            self.AddMatchString(re.compile(b'lock \?#00(1|0);'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'power \?#00(1|0);'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ATVSRC \?#00([0-9A-Fa-f]);'), self.__MatchSourceStatus, None)
            self.AddMatchString(re.compile(b'VideoIN \?#00([1-4]);'), self.__MatchVideoInput, None)
            self.AddMatchString(re.compile(b'volume \?#([0-9]{3});'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ER;'), self.__MatchError, None)

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Audio 1': 'AudioIN 001;',
            'Audio 2': 'AudioIN 002;',
            'Audio 3': 'AudioIN 003;',
            'Audio 4': 'AudioIN 004;',
            'AUX 1': 'AudioIN 005;',
            'AUX 2': 'AudioIN 006;',
            'MIC': 'AudioIN 007;',
            'Cancel Present Input Setup': 'AudioIN 008;'
        }

        AudioInputCmdString = ValueStateValues[value]
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def UpdateAudioInput(self, value, qualifier):

        AudioInputCmdString = 'AudioIN ?;'
        self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def __MatchAudioInput(self, match, tag):

        ValueStateValues = {
            '1': 'Audio 1',
            '2': 'Audio 2',
            '3': 'Audio 3',
            '4': 'Audio 4',
            '5': 'AUX 1',
            '6': 'AUX 2',
            '7': 'MIC',
            '8': 'Cancel Present Input Setup'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioInput', value, None)

    def SetEDID(self, value, qualifier):

        ValueStateValues = {
            '720p': 'EDID 001;',
            '1080i': 'EDID 002;',
            '1080p': 'EDID 003;',
            '4K@30Hz': 'EDID 004;',
            '4K@60Hz': 'EDID 005;',
            'LRN': 'EDID 006;'
        }

        EDIDCmdString = ValueStateValues[value]
        self.__SetHelper('EDID', EDIDCmdString, value, qualifier)

    def UpdateEDID(self, value, qualifier):

        EDIDCmdString = 'EDID ?;'
        self.__UpdateHelper('EDID', EDIDCmdString, value, qualifier)

    def __MatchEDID(self, match, tag):

        ValueStateValues = {
            '1': '720p',
            '2': '1080i',
            '3': '1080p',
            '4': '4K@30Hz',
            '5': '4K@60Hz',
            '6': 'LRN'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EDID', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'Lock 001;',
            'Off': 'Lock 000;'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'lock ?;'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'power 001;',
            'Off': 'power 000;'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'power ?;'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetReset(self, value, qualifier):

        ResetCmdString = 'reset 001;'
        self.__SetHelper('Reset', ResetCmdString, value, qualifier)

    def UpdateSourceStatus(self, value, qualifier):

        InputStates = ['1', '2', '3', '4']
        input_num = qualifier['Input']
        if input_num in InputStates:
            SourceStatusCmdString = 'ATVSRC ?;'
            self.__UpdateHelper('SourceStatus', SourceStatusCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def __MatchSourceStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Inactive'
        }

        temp_resVal = bin(int(match.group(1).decode(), 16))[2:].zfill(4)
        for i in range(0, 4):
            self.WriteStatus('SourceStatus', ValueStateValues[temp_resVal[i]], {'Input': str(i + 1)})

    def SetVideoInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'VideoIN 001;',
            'HDMI 2': 'VideoIN 002;',
            'HDMI 3': 'VideoIN 003;',
            'HDMI 4': 'VideoIN 004;'
        }

        VideoInputCmdString = ValueStateValues[value]
        self.__SetHelper('VideoInput', VideoInputCmdString, value, qualifier)

    def UpdateVideoInput(self, value, qualifier):

        VideoInputCmdString = 'VideoIN ?;'
        self.__UpdateHelper('VideoInput', VideoInputCmdString, value, qualifier)

    def __MatchVideoInput(self, match, tag):

        ValueStateValues = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoInput', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'volume {:03};'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'volume ?;'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        
        self.Send(commandstring)

            

    def __MatchError(self, match, tag):
        print('Error Occurred')

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
