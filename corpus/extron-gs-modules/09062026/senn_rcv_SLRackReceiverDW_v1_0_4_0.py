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
            'ActiveMatesStatus': {'Status': {}},
            'BatteryBars': {'Status': {}},
            'BatteryChargingStatus': {'Status': {}},
            'BatteryLifetime': {'Status': {}},
            'BatteryType': {'Status': {}},
            'BatteryVoltageLevel': {'Status': {}},
            'MuteSwitch': {'Status': {}},
            'OutputGain': {'Status': {}},
            'OutputLevel': {'Status': {}},
            'Pairing': {'Status': {}},
            'SoundProfile': {'Status': {}},
            'TransmitterType': {'Status': {}},
            'WarningStatus': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"mates":{"active":(\["tx1"]|\[])}}\x00'), self.__MatchActiveMatesStatus, None)
            self.AddMatchString(re.compile(b'{"mates":{"tx1":{"bat_bars":(\d+)}}}\x00'), self.__MatchBatteryBars, None)
            self.AddMatchString(re.compile(b'{"mates":{"tx1":{"bat_charging":(true|false)}}}\x00'), self.__MatchBatteryChargingStatus, None)
            self.AddMatchString(re.compile(b'{"mates":{"tx1":{"bat_lifetime":(\d+)}}}\x00'), self.__MatchBatteryLifetime, None)
            self.AddMatchString(re.compile(b'{"mates":{"tx1":{"bat_ type":([01])}}}\x00'), self.__MatchBatteryType, None)
            self.AddMatchString(re.compile(b'{"mates":{"tx1":{"bat_gauge":(\d+)}}}\x00'), self.__MatchBatteryVoltageLevel, None)
            self.AddMatchString(re.compile(b'{"rx1":{"mute_switch_active":(true|false)}}\x00'), self.__MatchMuteSwitch, None)
            self.AddMatchString(re.compile(b'{"audio":{"out1":{"gain_db":([0-6])}}}\x00'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'{"audio":{"out1":{"level_db":(-[1-5]?[0-9]|-60|0)}}}\x00'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'{"rx1":{"pair":(true|false)}}\x00'), self.__MatchPairing, None)
            self.AddMatchString(re.compile(b'{"audio":{"equalizer":{"preset":([0-4])}}}\x00'), self.__MatchSoundProfile, None)
            self.AddMatchString(re.compile(b'{"mates":{"tx1":{"device_type":([0-3])}}}\x00'), self.__MatchTransmitterType, None)
            self.AddMatchString(re.compile(b'{"rx1":{"warnings":\["([\s\S]+?)"]}}\x00'), self.__MatchWarningStatus, None)
            self.AddMatchString(re.compile(b'{"osc":{"error":.*([0-9]{3})[}\]]*\x00'), self.__MatchError, None)

    def UpdateActiveMatesStatus(self, value, qualifier):

        ActiveMatesStatusCmdString = '{"mates":{"active":null}}\r'
        self.__UpdateHelper('ActiveMatesStatus', ActiveMatesStatusCmdString, value, qualifier)

    def __MatchActiveMatesStatus(self, match, tag):

        ValueStateValues = {
            '["tx1"]': 'Yes',
            '[]': 'No'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ActiveMatesStatus', value, None)

    def UpdateBatteryBars(self, value, qualifier):

        BatteryBarsCmdString = '{"mates":{"tx1":{"bat_bars":null}}}\r'
        self.__UpdateHelper('BatteryBars', BatteryBarsCmdString, value, qualifier)

    def __MatchBatteryBars(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BatteryBars', value, None)

    def UpdateBatteryChargingStatus(self, value, qualifier):

        BatteryChargingStatusCmdString = '{"mates":{"tx1":{"bat_charging":null}}}\r'
        self.__UpdateHelper('BatteryChargingStatus', BatteryChargingStatusCmdString, value, qualifier)

    def __MatchBatteryChargingStatus(self, match, tag):

        ValueStateValues = {
            'true': 'Yes',
            'false': 'No'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BatteryChargingStatus', value, None)

    def UpdateBatteryLifetime(self, value, qualifier):

        BatteryLifetimeCmdString = '{"mates":{"tx1":{"bat_lifetime":null}}}\r'
        self.__UpdateHelper('BatteryLifetime', BatteryLifetimeCmdString, value, qualifier)

    def __MatchBatteryLifetime(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BatteryLifetime', value, None)

    def UpdateBatteryType(self, value, qualifier):

        BatteryTypeCmdString = '{"mates":{"tx1":{"bat_type":null}}}\r'
        self.__UpdateHelper('BatteryType', BatteryTypeCmdString, value, qualifier)

    def __MatchBatteryType(self, match, tag):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Rechargeable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BatteryType', value, None)

    def UpdateBatteryVoltageLevel(self, value, qualifier):

        BatteryVoltageLevelCmdString = '{"mates":{"tx1":{"bat_gauge":null}}}\r'
        self.__UpdateHelper('BatteryVoltageLevel', BatteryVoltageLevelCmdString, value, qualifier)

    def __MatchBatteryVoltageLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BatteryVoltageLevel', value, None)

    def SetMuteSwitch(self, value, qualifier):

        ValueStateValues = {
            'Enable': '{"rx1":{"mute_switch_active":true}}\r',
            'Disable': '{"rx1":{"mute_switch_active":false}}\r'
        }

        MuteSwitchCmdString = ValueStateValues[value]
        self.__SetHelper('MuteSwitch', MuteSwitchCmdString, value, qualifier)

    def UpdateMuteSwitch(self, value, qualifier):

        MuteSwitchCmdString = '{"rx1":{"mute_switch_active":null}}\r'
        self.__UpdateHelper('MuteSwitch', MuteSwitchCmdString, value, qualifier)

    def __MatchMuteSwitch(self, match, tag):

        ValueStateValues = {
            'true': 'Enable',
            'false': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteSwitch', value, None)

    def SetOutputGain(self, value, qualifier):

        ValueStateValues = {
            -24: 0,
            -18: 1,
            -12: 2,
            -6: 3,
            0: 4,
            6: 5,
            12: 6
        }

        if value in ValueStateValues:
            OutputGainCmdString = '{{"audio":{{"out1":{{"gain_db":{}}}}}}}\r'.format(ValueStateValues[value])
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        OutputGainCmdString = '{"audio":{"out1":{"gain_db":null}}}\r'
        self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)

    def __MatchOutputGain(self, match, tag):

        ValueStateValues = {
            '0': -24,
            '1': -18,
            '2': -12,
            '3': -6,
            '4': 0,
            '5': 6,
            '6': 12
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputGain', value, None)

    def UpdateOutputLevel(self, value, qualifier):

        OutputLevelCmdString = '{"audio":{"out1":{"level_db":null}}}\r'
        self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchOutputLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OutputLevel', value, None)

    def SetPairing(self, value, qualifier):

        ValueStateValues = {
            'Start': '{"rx1":{"pair":true}}\r',
            'Stop': '{"rx1":{"pair":false}}\r'
        }

        PairingCmdString = ValueStateValues[value]
        self.__SetHelper('Pairing', PairingCmdString, value, qualifier)

    def UpdatePairing(self, value, qualifier):

        PairingCmdString = '{"rx1":{"pair":null}}\r'
        self.__UpdateHelper('Pairing', PairingCmdString, value, qualifier)

    def __MatchPairing(self, match, tag):

        ValueStateValues = {
            'true': 'Start',
            'false': 'Stop'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Pairing', value, None)

    def SetSoundProfile(self, value, qualifier):

        ValueStateValues = {
            'Off': '{"audio":{"equalizer":{"preset":0}}}\r',
            'Female Speech': '{"audio":{"equalizer":{"preset":1}}}\r',
            'Male Speech': '{"audio":{"equalizer":{"preset":2}}}\r',
            'Media': '{"audio":{"equalizer":{"preset":3}}}\r',
            'Custom': '{"audio":{"equalizer":{"preset":4}}}\r'
        }

        SoundProfileCmdString = ValueStateValues[value]
        self.__SetHelper('SoundProfile', SoundProfileCmdString, value, qualifier)

    def UpdateSoundProfile(self, value, qualifier):

        SoundProfileCmdString = '{"audio":{"equalizer":{"preset":null}}}\r'
        self.__UpdateHelper('SoundProfile', SoundProfileCmdString, value, qualifier)

    def __MatchSoundProfile(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Female Speech',
            '2': 'Male Speech',
            '3': 'Media',
            '4': 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundProfile', value, None)

    def UpdateTransmitterType(self, value, qualifier):

        TransmitterTypeCmdString = '{"mates":{"tx1":{"device_type":null}}}\r'
        self.__UpdateHelper('TransmitterType', TransmitterTypeCmdString, value, qualifier)

    def __MatchTransmitterType(self, match, tag):

        ValueStateValues = {
            '0': 'Handheld',
            '1': 'Bodypack',
            '2': 'Tablestand',
            '3': 'Boundary'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TransmitterType', value, None)

    def UpdateWarningStatus(self, value, qualifier):

        WarningStatusCmdString = '{"rx1":{"warnings":null}}\r'
        self.__UpdateHelper('WarningStatus', WarningStatusCmdString, value, qualifier)

    def __MatchWarningStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('WarningStatus', value, None)

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
            self.counter = 0
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
