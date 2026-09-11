from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'AntennaRFLevelStatus': {'Parameters': ['Channel'], 'Status': {}},
            'AntennaStatus': {'Parameters': ['Channel'], 'Status': {}},
            'AudioLevelStatus': {'Parameters': ['Channel'], 'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryBars': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryChargeStatus': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryRemainingTime': {'Parameters': ['Channel'], 'Status': {}},
            'ChannelName': {'Parameters': ['Channel'], 'Status': {}},
            'ChannelStatus': {'Parameters': ['Channel'], 'Status': {}},
            'EncryptionMismatchWarning': {'Parameters': ['Channel'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Frequency': {'Parameters': ['Channel'], 'Status': {}},
            'GroupandChannel': {'Parameters': ['Receiver Channel', 'Group', 'Channel'], 'Status': {}},
            'GroupStatus': {'Parameters': ['Channel'], 'Status': {}},
            'InterferenceDetection': {'Parameters': ['Channel'], 'Status': {}},
            'MeterRate': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterMuteButtonStatus': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterMuteStatus': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterPowerSourceStatus': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterRFPower': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterType': {'Parameters': ['Channel'], 'Status': {}},
            'Volume': {'Parameters': ['Channel'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(rb'< SAMPLE ([1-4]) ALL (AX|XB|XX) (0\d\d|10\d|11[0-5]) (0[0-4]\d|050) >'), self.__MatchAntennaStatus, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) AUDIO_MUTE (ON|OFF) >'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) BATT_BARS (00[0-5]|255) >'), self.__MatchBatteryBars, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) BATT_CHARGE (0[0-9][0-9]|100) >'), self.__MatchBatteryChargeStatus, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) BATT_RUN_TIME (\d{5}) >'), self.__MatchBatteryRemainingTime, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) CHAN_NAME {?([\s\S]{8})}? >'), self.__MatchChannelName, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) ENCRYPTION_WARNING (ON|OFF) >'), self.__MatchEncryptionMismatchWarning, None)
            self.AddMatchString(compile(rb'< REP FW_VER {?([\s\S]{18})}? >'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) FREQUENCY (\d{6}) >'), self.__MatchFrequency, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) GROUP_CHAN (\d{2}),(\d{2}) >'), self.__MatchGroupStatus, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) RF_INT_DET (NONE|CRITICAL) >'), self.__MatchInterferenceDetection, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) METER_RATE (\d{5}) >'), self.__MatchMeterRate, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) TX_MUTE_BUTTON_STATUS (PRESSED|RELEASED|UNKN) >'), self.__MatchTransmitterMuteButtonStatus, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) TX_MUTE_STATUS (ON|OFF|UNKN) >'), self.__MatchTransmitterMuteStatus, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) TX_POWER_SOURCE (BATTERY|EXTERNAL|UNKN) >'), self.__MatchTransmitterPowerSourceStatus, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) TX_RF_PWR (LOW|NORMAL|HIGH|UNKN) >'), self.__MatchTransmitterRFPower, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) TX_TYPE (ULXD[1268]|UNKN|QLXD[12]) >'), self.__MatchTransmitterType, None)
            self.AddMatchString(compile(rb'< REP ([1-4]) AUDIO_GAIN (0[0-6][0-9]) >'), self.__MatchVolume, None)
            self.AddMatchString(compile(rb'< REP ([1-4])? ?([A-Z_]{21}|[A-Z_]{15}|[A-Z_]{6,11}) (252|253|254|65535|65534|65533|65532) >'), self.__MatchError, None)

    def __MatchAntennaStatus(self, match, tag):

        AntennaStateValues = {
            'AX': 'A on, B off',
            'XB': 'A off, B on',
            'XX': 'A off, B off',
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = AntennaStateValues[match.group(2).decode()]
        self.WriteStatus('AntennaStatus', value, qualifier)
        value = int(match.group(3).decode()) - 128
        self.WriteStatus('AntennaRFLevelStatus', value, qualifier)
        value = int(match.group(4).decode())
        self.WriteStatus('AudioLevelStatus', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            '1':   '1',
            '2':   '2',
            '3':   '3',
            '4':   '4',
            'All': '0',
        }

        ValueStateValues = {
            'On':     'ON',
            'Off':    'OFF',
            'Toggle': 'TOGGLE',
        }

        chan_val = qualifier['Channel']
        if chan_val in ChannelStates:
            AudioMuteCmdString = '< SET {0} AUDIO_MUTE {1} >'.format(ChannelStates[chan_val], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = ['1', '2', '3', '4']

        chan_val = qualifier['Channel']
        if chan_val in ChannelStates:
            AudioMuteCmdString = '< GET {0} AUDIO_MUTE >'.format(chan_val)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'ON':  'On',
            'OFF': 'Off',
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def UpdateBatteryBars(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            BatteryBarsCmdString = '< GET {0} BATT_BARS >'.format(chan_val)
            self.__UpdateHelper('BatteryBars', BatteryBarsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryBars')
        
    def __MatchBatteryBars(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = int(match.group(2).decode())
        value = 0 if value == 255 else value
        self.WriteStatus('BatteryBars', value, qualifier)

    def UpdateBatteryChargeStatus(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            BatteryChargeStatusCmdString = '< GET {0} BATT_CHARGE >'.format(chan_val)
            self.__UpdateHelper('BatteryChargeStatus', BatteryChargeStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryChargeStatus')

    def __MatchBatteryChargeStatus(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('BatteryChargeStatus', value, qualifier)

    def UpdateBatteryRemainingTime(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            BatteryRemainingTimeCmdString = '< GET {0} BATT_RUN_TIME >'.format(chan_val)
            self.__UpdateHelper('BatteryRemainingTime', BatteryRemainingTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryRemainingTime')

    def __MatchBatteryRemainingTime(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if value == 65535:
            self.WriteStatus('BatteryRemainingTime', 'Unknown', qualifier)
        else:
            hours = value // 60
            minutes = value % 60
            self.WriteStatus('BatteryRemainingTime', '{0}:{1:0>2}'.format(hours, minutes), qualifier)

    def UpdateChannelName(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            ChannelNameCmdString = '< GET {0} CHAN_NAME >'.format(chan_val)
            self.__UpdateHelper('ChannelName', ChannelNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelName')

    def __MatchChannelName(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = match.group(2).decode().strip()
        self.WriteStatus('ChannelName', value, qualifier)

    def UpdateChannelStatus(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            self.UpdateGroupStatus(None, {'Channel':chan_val})
        else:
            self.Discard('Invalid Command for UpdateChannelStatus')

    def UpdateEncryptionMismatchWarning(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            EncryptionMismatchWarningCmdString = '< GET {0} ENCRYPTION_WARNING >'.format(chan_val)
            self.__UpdateHelper('EncryptionMismatchWarning', EncryptionMismatchWarningCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEncryptionMismatchWarning')

    def __MatchEncryptionMismatchWarning(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off',
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('EncryptionMismatchWarning', value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '< GET FW_VER >'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode().strip()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetFrequency(self, value, qualifier):

        ChannelStates = {
            '1':   '1',
            '2':   '2',
            '3':   '3',
            '4':   '4',
            'All': '0',
        }

        ValueConstraints = {
            'Min': 450.000,
            'Max': 950.000,
            }

        chan_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and chan_val in ChannelStates:
            newValue = format(value, '.3f') 
            FrequencyCmdString = '< SET {0} FREQUENCY {1} >'.format(ChannelStates[chan_val], newValue.replace(".", ""))
            self.__SetHelper('Frequency', FrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFrequency')

    def UpdateFrequency(self, value, qualifier):

        ChannelStates = ['1', '2', '3', '4']

        chan_val = qualifier['Channel']
        if chan_val in ChannelStates:
            FrequencyCmdString = '< GET {0} FREQUENCY >'.format(chan_val)
            self.__UpdateHelper('Frequency', FrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFrequency')

    def __MatchFrequency(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        if 450000 <= int(match.group(2).decode()) <= 950000:
            value = str(int(match.group(2).decode()))
            float_value = float(value[:3]) + float('.' + value[3:])
            self.WriteStatus('Frequency', float_value, qualifier)

    def SetGroupandChannel(self, value, qualifier):

        ReceiverChannelStates = ['1', '2', '3', '4']

        GroupConstraints = {
            'Min': 1,
            'Max': 99,
        }

        ChannelConstraints = {
            'Min': 1,
            'Max': 99,
        }

        rx_chan_val = qualifier['Receiver Channel']
        group_val = qualifier['Group']
        chan_val = qualifier['Channel']
        
        if (ChannelConstraints['Min'] <= chan_val <= ChannelConstraints['Max'] and
                GroupConstraints['Min'] <= group_val <= GroupConstraints['Max'] and
                rx_chan_val in ReceiverChannelStates):
            GroupandChannelCmdString = '< SET {0} GROUP_CHAN {1:02d},{2:02d} >'.format(rx_chan_val, group_val, chan_val)
            self.__SetHelper('GroupandChannel', GroupandChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupandChannel')

    def UpdateGroupStatus(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            GroupStatusCmdString = '< GET {0} GROUP_CHAN >'.format(chan_val)
            self.__UpdateHelper('GroupStatus', GroupStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupStatus')

    def __MatchGroupStatus(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = int(match.group(2).decode())
        value2 = int(match.group(3).decode())
        self.WriteStatus('ChannelStatus', value2, qualifier)
        self.WriteStatus('GroupStatus', value, qualifier)

    def UpdateInterferenceDetection(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            InterferenceDetectionCmdString = '< GET {0} RF_INT_DET >'.format(chan_val)
            self.__UpdateHelper('InterferenceDetection', InterferenceDetectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInterferenceDetection')

    def __MatchInterferenceDetection(self, match, tag):

        ValueStateValues = {
            'NONE': 'None',
            'CRITICAL': 'Critical'
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InterferenceDetection', value, qualifier)

    def SetMeterRate(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': '0'
        }

        speed = value if 100 <= value <= 99999 else 0
        MeterRateCmdString = '< SET {0} METER_RATE {1:05d} >'.format(ChannelStates[qualifier['Channel']], speed)
        self.__SetHelper('MeterRate', MeterRateCmdString, value, qualifier)

    def __MatchMeterRate(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = int(match.group(2).decode()) if 100 <= int(match.group(2).decode()) <= 99999 else 0
        self.WriteStatus('MeterRate', value, qualifier)
        if value == 0:
            self.WriteStatus('AntennaStatus', 'None', qualifier)

    def UpdateTransmitterMuteButtonStatus(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            TransmitterMuteButtonStatusCmdString = '< GET {0} TX_MUTE_BUTTON_STATUS >'.format(chan_val)
            self.__UpdateHelper('TransmitterMuteButtonStatus', TransmitterMuteButtonStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterMuteButtonStatus')

    def __MatchTransmitterMuteButtonStatus(self, match, tag):

        ValueStateValues = {
            'PRESSED':  'Pressed',
            'RELEASED': 'Released',
            'UNKN':     'Unknown',
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterMuteButtonStatus', value, qualifier)

    def UpdateTransmitterMuteStatus(self, value, qualifier):

        chan_val = qualifier['Channel']

        if 1 <= int(chan_val) <= 4:
            TransmitterMuteStatusCmdString = '< GET {0} TX_MUTE_STATUS >'.format(chan_val)
            self.__UpdateHelper('TransmitterMuteStatus', TransmitterMuteStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterMuteStatus')

    def __MatchTransmitterMuteStatus(self, match, tag):

        ValueStateValues = {
            'ON':   'On',
            'OFF':  'Off',
            'UNKN': 'Unknown'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterMuteStatus', value, qualifier)

    def UpdateTransmitterPowerSourceStatus(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            TransmitterPowerSourceStatusCmdString = '< GET {0} TX_POWER_SOURCE >'.format(chan_val)
            self.__UpdateHelper('TransmitterPowerSourceStatus', TransmitterPowerSourceStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterPowerSourceStatus')

    def __MatchTransmitterPowerSourceStatus(self, match, tag):

        ValueStateValues = {
            'BATTERY':  'Battery',
            'EXTERNAL': 'External',
            'UNKN':     'Unknown',
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterPowerSourceStatus', value, qualifier)

    def UpdateTransmitterRFPower(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            TransmitterRFPowerCmdString = '< GET {0} TX_RF_PWR >'.format(chan_val)
            self.__UpdateHelper('TransmitterRFPower', TransmitterRFPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterRFPower')

    def __MatchTransmitterRFPower(self, match, tag):

        ValueStateValues = {
            'LOW':    'Low',
            'NORMAL': 'Normal',
            'HIGH':   'High',
            'UNKN':   'Unknown',
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterRFPower', value, qualifier)

    def UpdateTransmitterType(self, value, qualifier):

        chan_val = qualifier['Channel']
        if 1 <= int(chan_val) <= 4:
            TransmitterTypeCmdString = '< GET {0} TX_TYPE >'.format(chan_val)
            self.__UpdateHelper('TransmitterType', TransmitterTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterType')

    def __MatchTransmitterType(self, match, tag):

        ValueStateValues = {
            'ULXD1': 'ULXD 1',
            'ULXD2': 'ULXD 2',
            'ULXD6': 'ULXD 6',
            'ULXD8': 'ULXD 8',
            'QLXD1': 'QLXD 1',
            'QLXD2': 'QLXD 2',
            'UNKN':  'Unknown',
        }

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterType', value, qualifier)

    def SetVolume(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': '0',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 60,
            }

        chan_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and chan_val in ChannelStates:
            VolumeCmdString = '< SET {0} AUDIO_GAIN {1:03d} >'.format(ChannelStates[chan_val], value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ChannelStates = ['1', '2', '3', '4']
        
        chan_val = qualifier['Channel']
        if chan_val in ChannelStates:
            VolumeCmdString = '< GET {0} AUDIO_GAIN >'.format(chan_val)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 60:
            self.WriteStatus('Volume', value, qualifier)

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
        self.counter = 0

        if match.group(1):
            self.Error(['Error Channel: {0}, Command: {1}, Code: {2}'.format(match.group(1).decode(),
                                                                             match.group(2).decode(),
                                                                             match.group(3).decode())])
        else:
            self.Error(['Error Command: {0}, Code: {1}'.format(match.group(2).decode(), match.group(3).decode())])

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}


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

