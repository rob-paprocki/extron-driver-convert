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
            'BatteryGauge': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'MateActive': {'Status': {}},
            'MuteActive': {'Status': {}},
            'OutputGain': {'Status': {}},
            'OutputMode': {'Status': {}},
            'Pair': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"mates":{"tx1":{"bat_gauge":([0-9]{1,3})\}\}\}\x00'), self.__MatchBatteryGauge, None)
            self.AddMatchString(re.compile(b'{"device":{"state":([0-4])\}\}\x00'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'{"device":{"identity":{"version":"(\d+\.\d+\.\d+)"\}\}\}\x00'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'{"mates":{"active":\[(("tx1")?)\]\}\}\x00'), self.__MatchMateActive, None)
            self.AddMatchString(re.compile(b'{"rx1":{"mute_switch_active":(true|false)\}\}\x00'), self.__MatchMuteActive, None)
            self.AddMatchString(re.compile(b'{"audio":{"out1":{"gain_db":([0-9]{1,2})\}\}\}\x00'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'{"audio":{"out1":{"type":(1|2)\}\}\}\x00'), self.__MatchOutputMode, None)
            self.AddMatchString(re.compile(b'{"osc":{"error":.*([0-9]{3})[\}\]]*\x00'), self.__MatchError, None)

    def UpdateBatteryGauge(self, value, qualifier):

        BatteryGaugeCmdString = '{"mates":{"tx1":{"bat_gauge":null}}}\r'
        self.__UpdateHelper('BatteryGauge', BatteryGaugeCmdString, value, qualifier)

    def __MatchBatteryGauge(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BatteryGauge', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '{"device":{"state":null}}\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Pairing',
            '2': 'Receiver Update',
            '3': 'Transmitter Update',
            '4': 'Transmitter Update Confirmation'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '{"device":{"identity":{"version":null}}}\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def UpdateMateActive(self, value, qualifier):

        MateActiveCmdString = '{"mates":{"active":null}}\r'
        self.__UpdateHelper('MateActive', MateActiveCmdString, value, qualifier)

    def __MatchMateActive(self, match, tag):

        ValueStateValues = {
            '"tx1"': 'Yes',
            '': 'No'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MateActive', value, None)

    def SetMuteActive(self, value, qualifier):

        ValueStateValues = {
            'Yes': '{"rx1":{"mute_switch_active":true}}\r',
            'No': '{"rx1":{"mute_switch_active":false}}\r'
        }
        MuteActiveCmdString = ValueStateValues[value]
        self.__SetHelper('MuteActive', MuteActiveCmdString, value, qualifier)

    def UpdateMuteActive(self, value, qualifier):

        MuteActiveCmdString = '{"rx1":{"mute_switch_active":null}}\r'
        self.__UpdateHelper('MuteActive', MuteActiveCmdString, value, qualifier)

    def __MatchMuteActive(self, match, tag):

        ValueStateValues = {
            'true': 'Yes',
            'false': 'No'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteActive', value, None)

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 30
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputGainCmdString = '{{"audio":{{"out1":{{"gain_db":{}}}}}}}\r'.format(value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        OutputGainCmdString = '{"audio":{"out1":{"gain_db":null}}}\r'
        self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)

    def __MatchOutputGain(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OutputGain', value, None)

    def SetOutputMode(self, value, qualifier):

        ValueStateValues = {
            'Line': '{"audio":{"out1":{"type":2}}}\r',
            'Mic': '{"audio":{"out1":{"type":1}}}\r'
        }
        OutputModeCmdString = ValueStateValues[value]
        self.__SetHelper('OutputMode', OutputModeCmdString, value, qualifier)

    def UpdateOutputMode(self, value, qualifier):

        OutputModeCmdString = '{"audio":{"out1":{"type":null}}}\r'
        self.__UpdateHelper('OutputMode', OutputModeCmdString, value, qualifier)

    def __MatchOutputMode(self, match, tag):

        ValueStateValues = {
            '2': 'Line',
            '1': 'Mic'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputMode', value, None)

    def SetPair(self, value, qualifier):

        ValueStateValues = {
            'Enable': '{"rx1":{"pair":true}}\r',
            'Disable': '{"rx1":{"pair":false}}\r'
        }
        PairCmdString = ValueStateValues[value]
        self.__SetHelper('Pair', PairCmdString, value, qualifier)

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

        Errors = {
            '400': 'Error 400: Bad Request',
            '401': 'Error 401: Unauthorized',
            '403': 'Error 403: Forbidden',
            '404': 'Error 404: Not Found',
            '406': 'Error 406: Not Acceptable',
            '408': 'Error 408: Request Timeout',
            '409': 'Error 409: Conflict',
            '410': 'Error 410: Gone',
            '413': 'Error 413: Request Entity Too Large',
            '414': 'Error 414: Request Too Complex',
            '422': 'Error 422: Unprocessable Entity',
            '423': 'Error 423: Locked',
            '424': 'Error 424: Failed Dependency',
            '450': 'Error 450: Answer Too Long',
            '454': 'Error 454: Parameter Address Not Found',
            '500': 'Error 500: Internal Server Error',
            '501': 'Error 501: Not Implemented',
            '503': 'Error 503: Service Unavailable'
        }
        value = match.group(1).decode()
        if value in Errors:
            self.Error([Errors[value]])

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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
