from extronlib.interface import EthernetClientInterface
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
            'ARMC': {'Status': {}},
            'LEDLightControl': {'Parameters': ['Channel', 'Color'], 'Status': {}},
            'LoadPreset': {'Status': {}},
            'PhantomPower': {'Parameters': ['Channel'], 'Status': {}},
            'SavePreset': {'Status': {}},
            'SwitchLogicStatus': {'Parameters': ['Channel'], 'Status': {}},
        }

        self.Initial = True
        self._IPAddress = None
        self._ListeningPort = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ACK GARMC (0|1)\r'), self.__MatchARMC, None)
            self.AddMatchString(re.compile(b'ACK GCH32 0 CH1R=(0|1) CH1G=(0|1) CH1SC=[0-1] CH2R=(0|1) CH2G=(0|1) CH2SC=[0-1] CH3R=(0|1) CH3G=(0|1) CH3SC=[0-1] CH4R=(0|1) CH4G=(0|1) CH4SC=[0-1]\r'), self.__MatchLEDLightControl, None)
            self.AddMatchString(re.compile(b'ACK QUERY PP1=(0|1) PP2=(0|1) PP3=(0|1) PP4=(0|1) ID=(0|1)\r'), self.__MatchPhantomPower, None)
            self.AddMatchString(re.compile(b'BSTATUS B(1|2|3|4)=(0|1)\r'), self.__MatchSwitchLogicStatus, None)
            self.AddMatchString(re.compile(b'NACK'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'ACK SASIP [0-9.]{7,15}:[0-9]{1,5}\r'), self.__MatchSubscribe, None)

    @property
    def IPAddr(self):
        return self._IPAddress

    @IPAddr.setter
    def IPAddr(self, value):
        match = re.match('\d+\.\d+\.\d+\.\d+', str(value))
        if match:
            self._IPAddress = str(value)
        else:
            print('IP Address parameter is wrong.')

    @property
    def ListeningPort(self):
        return self._ListeningPort

    @ListeningPort.setter
    def ListeningPort(self, value):
        if 1 <= int(value) <= 65535:
            self._ListeningPort = int(value)

    def __MatchSubscribe(self, match, qualifier):
        self.Initial = False

    def SetARMC(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        ARMCCmdString = 'SARMC {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ARMC', ARMCCmdString, value, qualifier)

    def UpdateARMC(self, value, qualifier):

        ARMCCmdString = 'GARMC\r'
        self.__UpdateHelper('ARMC', ARMCCmdString, value, qualifier)

    def __MatchARMC(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ARMC', value, None)

    def UpdateLEDLightControl(self, value, qualifier):
        LEDLightControlCmdString = 'GCH32 0\r'
        self.__UpdateHelper('LEDLightControl', LEDLightControlCmdString, value, qualifier)

    def __MatchLEDLightControl(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        qualifier1R = {'Channel': '1', 'Color': 'Red'}
        qualifier1G = {'Channel': '1', 'Color': 'Green'}

        value1R = ValueStateValues[match.group(1).decode()]
        value1G = ValueStateValues[match.group(2).decode()]

        self.WriteStatus('LEDLightControl', value1R, qualifier1R)
        self.WriteStatus('LEDLightControl', value1G, qualifier1G)

        qualifier2R = {'Channel': '2', 'Color': 'Red'}
        qualifier2G = {'Channel': '2', 'Color': 'Green'}

        value2R = ValueStateValues[match.group(3).decode()]
        value2G = ValueStateValues[match.group(4).decode()]

        self.WriteStatus('LEDLightControl', value2R, qualifier2R)
        self.WriteStatus('LEDLightControl', value2G, qualifier2G)

        qualifier3R = {'Channel': '3', 'Color': 'Red'}
        qualifier3G = {'Channel': '3', 'Color': 'Green'}

        value3R = ValueStateValues[match.group(5).decode()]
        value3G = ValueStateValues[match.group(6).decode()]

        self.WriteStatus('LEDLightControl', value3R, qualifier3R)
        self.WriteStatus('LEDLightControl', value3G, qualifier3G)

        qualifier4R = {'Channel': '4', 'Color': 'Red'}
        qualifier4G = {'Channel': '4', 'Color': 'Green'}

        value4R = ValueStateValues[match.group(7).decode()]
        value4G = ValueStateValues[match.group(8).decode()]

        self.WriteStatus('LEDLightControl', value4R, qualifier4R)
        self.WriteStatus('LEDLightControl', value4G, qualifier4G)

    def SetLEDLightControl(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': '0'
        }

        ColorStates = {
            'Red': 'R=',
            'Green': 'G='
        }

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        channel = ChannelStates[qualifier['Channel']]
        color = ColorStates[qualifier['Color']]

        LEDLightControlCmdString = 'SCH32 {0} {1}{2}\r'.format(channel, color, ValueStateValues[value])
        self.__SetHelper('LEDLightControl', LEDLightControlCmdString, value, qualifier)

    def SetLoadPreset(self, value, qualifier):

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
            '9': '9'
        }

        LoadPresetCmdString = 'LOAD {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LoadPreset', LoadPresetCmdString, value, qualifier)

    def SetPhantomPower(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': '0'
        }

        StateStateValues = {
            'Off': '0',
            'On': '1'
        }

        PhantomPowerCmdString = 'PP {0} {1}\r'.format(ChannelStates[qualifier['Channel']], StateStateValues[value])
        self.__SetHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)

    def UpdatePhantomPower(self, value, qualifier):
        PhantomPowerCmdString = 'QUERY\r'
        self.__UpdateHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)

    def __MatchPhantomPower(self, match, tag):

        StateStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        for i in range(1, 5):
            qualifier = {'Channel': str(i)}
            value = StateStateValues[match.group(i).decode()]
            self.WriteStatus('PhantomPower', value, qualifier)

    def SetSavePreset(self, value, qualifier):

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
            '9': '9'
        }

        SavePresetCmdString = 'SAVE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)

    def __MatchSwitchLogicStatus(self, match, tag):

        SwitchLogicState = {
            '1': 'On',
            '0': 'Off'
        }

        value = SwitchLogicState[match.group(2).decode()]
        self.WriteStatus('SwitchLogicStatus', value, {'Channel': match.group(1).decode()})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Initial:
            self.Send('SASIP {0}:{1}\r'.format(self._IPAddress, self._ListeningPort))
            @Wait(3)
            def initialize():
                self.Send(commandstring)
        else:
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

            if self.Initial:
                self.Send('SASIP {0}:{1}\r'.format(self._IPAddress, self._ListeningPort))
                @Wait(3)
                def initialize():
                    self.Send(commandstring)
            else:
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
        self.Initial = True

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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=49494, Model=None):
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
