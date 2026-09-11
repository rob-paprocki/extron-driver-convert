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
            'AudioMute': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'mute=(on|off)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'videofreeze=(on|off)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'input=(hdmi1|hdmi2|dp1|vga1|ops1)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'powerstate=(on|off|standby|ready|powersave|updateon|updateready)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'volume=([0-9]{1,2}|100)\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'invalid cmd'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        self.__SetHelper('AudioMute', 'set mute={}\r'.format(value.lower()), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'get mute\r', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AudioMute', value, None)

    def SetFreeze(self, value, qualifier):

        self.__SetHelper('Freeze', 'set videofreeze={}\r'.format(value.lower()), value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        self.__UpdateHelper('Freeze', 'get videofreeze\r', value, qualifier)

    def __MatchFreeze(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        state = {'HDMI 1': 'hdmi1', 'HDMI 2': 'hdmi2', 'DisplayPort': 'dp1', 'VGA': 'vga1', 'OPS': 'ops1'}[value]
        self.__SetHelper('Input', 'set input={}\r'.format(state), value, qualifier)

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', 'get input\r', value, qualifier)

    def __MatchInput(self, match, tag):

        value = {'hdmi1': 'HDMI 1', 'hdmi2': 'HDMI 2', 'dp1': 'DisplayPort', 'vga1': 'VGA', 'ops1': 'OPS'}[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        state = {'On': 'on', 'Off': 'off', 'Ready': 'ready', 'Power Save': 'powersave'}[value]
        self.__SetHelper('Power', 'set powerstate={}\r'.format(state), value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'get powerstate\r', value, qualifier)

    def __MatchPower(self, match, tag):

        value = {
            'on': ['On', 'Normal'],
            'off': ['Off', 'Normal'],
            'standby': ['Off', 'Low Power'],
            'ready': ['Ready', 'Normal'],
            'powersave': ['Power Save', 'Low Power'],
            'updateon': ['On', 'Updating'],
            'updateready': ['Ready', 'Updating']
        }[match.group(1).decode()]

        self.WriteStatus('Power', value[0], None)
        self.WriteStatus('DeviceStatus', value[1], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', 'set volume={}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get volume\r'
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
        self.Error(['Invalid Command'])

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
